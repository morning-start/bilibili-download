import asyncio
from pathlib import Path
from typing import Callable

from bilibili_api import Credential

from utils.collection import download_collection
from utils.preparation import make_dir, read_credential, read_download
from utils.series import download_channel_series
from utils.video import download_file


async def multi_fn(
    credential: Credential,
    config_list: list[dict],
    id_name: str,
    download_fn: Callable[[str, str, Credential, bool], None],
    download_dir: str = "./out",
):
    for config in config_list:
        id = config[id_name]  # 缺失id报错
        out_dir = config.get("out_dir", download_dir)
        download_video = config.get("download_video", True)
        # print(bool(download_video))

        await download_fn(id, out_dir, credential, download_video)


async def main():
    config_path = Path("./config/cookie.json")
    # 生成一个 Credential 对象
    cred = await read_credential(config_path)
    cred = None
    config = read_download(Path("./config/download.json"))
    download_dir = config.get("download_dir", "./out")
    config_map = {
        "favorite_list": {"id": "fid", "fn": download_collection},
        "video_list": {"id": "bvid", "fn": download_file},
        "channel_list": {"id": "sid", "fn": download_channel_series},
    }
    # for k, v in config_map.items():
    #     link_list = config.get(k, [])
    #     await multi_fn(cred, link_list, v["id"], v["fn"], download_dir)
    k, v = list(config_map.items())[2]
    link_list = config.get(k, [])
    await multi_fn(cred, link_list, v["id"], v["fn"], download_dir)


if __name__ == "__main__":
    make_dir()
    asyncio.run(main())
