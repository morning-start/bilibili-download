from pathlib import Path

import httpx
from bilibili_api import HEADERS, Credential, video
from tqdm import tqdm

from ffmpeg import FFmpeg

"""
B站下载有2种格式
1. 视频.m4s+音频.m4s
2. 视频.flv
"""


def convert_audio(audio_path: str, out_path: str):
    ffmpeg = FFmpeg()
    ffmpeg.input(audio_path).output(out_path, {"c:a": "copy"})
    ffmpeg.execute()
    Path(audio_path).unlink()


def convert_video(temp_list: list, out_path: str):
    """
    temp_list: 临时文件列表
    out_path: 输出文件路径
    """
    ffmpeg = FFmpeg()
    if len(temp_list) == 1:
        ffmpeg.input(temp_list[0]).output(out_path)
    if len(temp_list) == 2:
        ffmpeg.input(temp_list[0]).input(temp_list[1]).output(out_path, {"c": "copy"})
    # print(ffmpeg.arguments)
    ffmpeg.execute()
    for temp in temp_list:
        Path(temp).unlink()


async def download_url(url: str, out: str, info: str):
    # 下载函数
    async with httpx.AsyncClient(headers=HEADERS) as sess:
        resp = await sess.get(url)
        length = int(resp.headers.get("content-length"))
        chunk_n = 1024 * 1024
        # 向上取整
        length = (length + chunk_n - 1) // chunk_n
        with open(out, "wb") as f:
            iter_bytes = tqdm(resp.iter_bytes(chunk_n), total=length, desc=info)
            for chunk in iter_bytes:
                if not chunk:
                    break

                f.write(chunk)


async def download_video(
    detecter: video.VideoDownloadURLDataDetecter,
    streams: list[video.VideoStreamDownloadURL | video.AudioStreamDownloadURL],
    file_name: str,
) -> list[str]:
    """
    下载视频
    :param detecter: 视频下载信息检测器
    :param streams: 视频流下载链接
    :param file_name: 文件名
    :return: list 下载完成的文件路径
    """

    if detecter.check_flv_stream():
        temp_video = f".temp/{file_name}.flv"
        # FLV 流下载
        if not Path(temp_video).exists():
            await download_url(streams[0].url, temp_video, "FLV 音视频流")
        return [temp_video]
    else:
        # MP4 流下载
        temp_video = f"./temp/video_{file_name}.m4s"
        temp_audio = f"./temp/audio_{file_name}.m4s"
        if not Path(temp_video).exists():
            await download_url(streams[0].url, temp_video, "视频流")
        if not Path(temp_audio).exists():
            await download_url(streams[1].url, temp_audio, "音频流")
        return [temp_video, temp_audio]


async def download_audio(
    detecter: video.VideoDownloadURLDataDetecter,
    streams: list[video.VideoStreamDownloadURL | video.AudioStreamDownloadURL],
    file_name: str,
) -> str:
    """
    下载音频
    :param detecter: 视频下载信息检测器
    :param streams: 视频流下载链接
    :param file_name: 文件名
    :return:str 下载完成的文件路径
    """
    if detecter.check_flv_stream():
        temp_audio = f".temp/{file_name}.flv"
        # FLV 流下载
        if not Path(temp_audio).exists():
            await download_url(streams[0].url, temp_audio, "FLV 音视频流")
    else:
        # MP4 流下载
        temp_audio = f"./temp/audio_{file_name}.m4s"
        # 将 file_name 中的/识别为字符串

        if not Path(temp_audio).exists():
            # 去除非法字符
            await download_url(streams[1].url, temp_audio, "音频流")
    return temp_audio


async def get_video_info(bv_id, credential):
    v = video.Video(bvid=bv_id, credential=credential)
    info = await v.get_info()
    file_name: str = info["title"]
    file_name = file_name.replace("/", " ")
    download_url_data = await v.get_download_url(0)
    return file_name, download_url_data


async def download_file(
    bv_id: str,
    out_dir: str,
    credential: Credential = None,
    d_v: bool = False,
):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    # 实例化 Video 类
    file_name, download_url_data = await get_video_info(bv_id, credential)
    # 解析视频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_best_streams()
    if d_v:
        out_path = f"{out_dir}/{file_name}.mp4"
        if Path(out_path).exists():
            return
        temp_list = await download_video(detecter, streams, file_name)
        convert_video(temp_list, out_path)
    else:
        out_path = Path(f"{out_dir}/{file_name}.aac")
        if out_path.exists():
            return
        audio_path = await download_audio(detecter, streams, file_name)
        convert_audio(audio_path, out_path)
