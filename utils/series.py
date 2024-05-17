from bilibili_api import Credential
from bilibili_api.channel_series import ChannelSeries
from tqdm import tqdm

from utils.video import download_file


async def get_series(sid: str, cred: Credential = None) -> tuple[str, int, list[dict]]:
    """
    获取频道

    Parameters:
    ---
    sid: str
        频道id，channel/seriesdetail?sid=3164316 中的sid
    cred: Credential
        用户认证信息。默认是None，只能获取公开的频道

    Returns:
    ---
    name: str
        频道名称
    total: int
        频道视频总数
    video_infos: list[dict]
        频道视频信息列表

    """

    cs = ChannelSeries(id_=sid, credential=cred)
    res = await cs.get_videos()
    video_infos: list[dict] = res.get("archives")
    meta = cs.get_meta()
    name = meta.get("name")
    total = meta.get("total")
    # bvid_list = [video_info.get("bvid") for video_info in video_infos]
    return name, total, video_infos


def parse_video_info(v: dict[str]):
    file_name = v.get("title")
    bvid = v.get("bvid")
    cover = v.get("cover")
    return {"file_name": file_name, "bvid": bvid}


async def download_channel_series(
    sid: str,
    out_dir: str,
    credential: Credential = None,
    download_video=True,
):
    series_name, media_count, medias = await get_series(sid, cred=credential)
    iter_medias = tqdm(medias, total=media_count, desc=f"🚀{series_name}")
    for v in iter_medias:
        info = parse_video_info(v)
        bvid = info.get("bvid")
        # file_name = info.get("file_name")

        await download_file(
            bvid,
            f"{out_dir}/{series_name}",
            credential,
            download_video,
        )
