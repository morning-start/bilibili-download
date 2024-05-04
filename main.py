import asyncio
import json
import re
from pathlib import Path

from bilibili_api import Credential

from utils.collection import download_collection


def get_bvid(url: str):
    bvid = re.search(r"BV[0-9a-zA-Z]{10}", url)

    return bvid.group()


def read_credential(file_path: Path) -> Credential:
    """
    读取配置文件
    :param file_path: 配置文件路径
    :return: Credential 对象
    """
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件 {file_path} 不存在")
    with open(file_path, "r", encoding="utf-8") as f:
        data: dict = json.load(f)

    return Credential(
        sessdata=data.get("SESSDATA"),
        bili_jct=data.get("bili_jct"),
        buvid3=data.get("buvid3"),
    )


def read_download(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件 {file_path} 不存在")
    with open(file_path, "r", encoding="utf-8") as f:
        data: dict = json.load(f)
    return data


if __name__ == "__main__":
    config_path = Path("./config/cookie.json")
    # 生成一个 Credential 对象
    credential = read_credential(config_path)
    config = read_download(Path("./config/download.json"))
    asyncio.run(download_collection(credential=credential, **config))
