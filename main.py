import asyncio
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bilibili_api import Credential
from DrissionPage import ChromiumOptions, ChromiumPage

from utils.collection import download_collection
from utils.video import download_v


def get_id(url: str) -> dict:
    result = urlparse(url)
    res = {}
    p = result.path.strip("/")
    query_params = parse_qs(result.query)
    if "BV" in p:
        bvid = p.split("/")[-1]
        res["bvid"] = bvid
    elif "favlist" in p:
        fid = query_params["fid"][0]
        res["fid"] = fid
    elif "channel" in p:
        sid = query_params["sid"][0]
        res["sid"] = sid
    return res


def get_cookies() -> dict:
    opt = ChromiumOptions()
    opt.headless()
    page = ChromiumPage(opt)
    page.get("https://www.bilibili.com/")
    cookies = page.cookies()
    page.close()
    c = {}
    for i in cookies:
        c[i["name"]] = i["value"]
    return c


async def read_credential(file_path: Path) -> Credential:
    """
    读取配置文件
    :param file_path: 配置文件路径
    :return: Credential 对象
    """
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件 {file_path} 不存在")
    with open(file_path, "r", encoding="utf-8") as f:
        data: dict = json.load(f)
    cred = Credential(
        sessdata=data.get("SESSDATA"),
        bili_jct=data.get("bili_jct"),
        buvid3=data.get("buvid3"),
    )
    try:
        if not await cred.check_valid():
            await cred.refresh()
    except Exception:
        cookies = get_cookies()
        if cookies:
            cred = Credential.from_cookies(cookies)
            with open(file_path, "w") as f:
                f.write(json.dumps(cookies))
        else:
            cred = None

    return cred


def read_download(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件 {file_path} 不存在")
    with open(file_path, "r", encoding="utf-8") as f:
        data: list = json.load(f)
    return data


async def multi_favorite(
    credential: Credential, config_list: list[dict], download_dir: str
):
    for config in config_list:
        fid = config["fid"]  # 缺失fid报错
        out_dir = config.get("out_dir", download_dir)
        download_video = config.get("download_video", True)
        await download_collection(fid, out_dir, credential, download_video)


async def multi_video(
    credential: Credential, config_list: list[dict], download_dir: str
):
    for config in config_list:
        bvid = config["bvid"]  # 缺失bv_id报错
        out_dir = config.get("out_dir", download_dir)
        download_video = config.get("download_video", True)
        download_v(bvid, out_dir, credential, download_video)


async def main():
    config_path = Path("./config/cookie.json")
    # 生成一个 Credential 对象
    credential = await read_credential(config_path)
    config = read_download(Path("./config/download.json"))
    download_dir = config.get("download_dir", "./out")
    favorite_list = config.get("favorite_list", [])
    video_list = config.get("video_list", [])
    channel_series = config.get("channel_list", [])
    await multi_favorite(credential, favorite_list, download_dir)
    await multi_video(credential, video_list, download_dir)


if __name__ == "__main__":
    asyncio.run(main())
