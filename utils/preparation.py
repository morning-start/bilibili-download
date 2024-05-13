import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bilibili_api import Credential
from DrissionPage import ChromiumOptions, ChromiumPage


def make_dir():
    Path("./out").mkdir(exist_ok=True)
    Path("./temp").mkdir(exist_ok=True)


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
        cookies = _get_cookies()
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


# def read_urls(file_path: Path) -> list[str]:
#     if not file_path.exists():
#         raise FileNotFoundError(f"配置文件 {file_path} 不存在")
#     with open(file_path, "r", encoding="utf-8") as f:
#         data: list = json.load(f)
#     return data


# def write_download_config(file_path: Path, urls: list[str]):
#     if not file_path.exists():
#         raise FileNotFoundError(f"配置文件 {file_path} 不存在")
#     config = read_download(file_path)
#     for url in urls:
#         data = _generate_download_config(url)
#         config = _merge_config(config, data)

#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(config, f, indent=4)


def _get_cookies() -> dict:
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


def _get_id(url: str) -> dict:
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


def generate_download_config(
    url: str, out_dir: str = None, download_video: bool = None
):
    id_map = _get_id(url)
    mapping = {
        "bvid": "video_list",
        "fid": "favorite_list",
        "sid": "channel_series",
    }
    if not id_map:
        raise ValueError("URL 无效")
    res = {}
    id_name = list(id_map.keys())[0]
    list_name = mapping[id_name]

    res[id_name] = id_map[id_name]
    if out_dir:
        res["out_dir"] = out_dir
    if download_video is not None:
        res["download_video"] = download_video
    return {
        list_name: [res],
    }


def _merge_config(config: dict[str, list], data: dict[str, list]):
    list_name = list(data.keys())[0]
    config.setdefault(list_name, [])
    config[list_name].extend(data[list_name])
    return config
