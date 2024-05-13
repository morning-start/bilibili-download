from bilibili_api import Credential, favorite_list
from tqdm import tqdm

from utils.video import download_v


async def get_collection(
    fid: str, media_count: int, cre: Credential = None
) -> list[dict]:
    res = []
    each_page = 20
    max_page = (media_count + each_page - 1) // each_page
    for page in range(1, max_page + 1):
        resp = await favorite_list.get_video_favorite_list_content(
            media_id=fid, page=page, credential=cre
        )
        medias: list = resp.get("medias")
        res.extend(medias)
    return res


async def get_collection_info(fid: str, cre: Credential = None):
    resp = await favorite_list.get_video_favorite_list_content(
        media_id=fid, credential=cre
    )
    info: dict = resp.get("info")
    count = info.get("media_count")
    collection_name = info.get("title")
    return int(count), collection_name


def get_video_info(v: dict[str]):
    file_name = v.get("title")
    bvid = v.get("bvid")
    cover = v.get("cover")
    return {"file_name": file_name, "bvid": bvid}


async def download_collection(
    fid, out_dir, credential: Credential, download_video=True
):
    media_count, collection_name = await get_collection_info(fid=fid, cre=credential)
    medias = await get_collection(fid=fid, media_count=media_count, cre=credential)
    iter_medias = tqdm(medias, total=media_count, desc=f"🚀{collection_name}")
    for v in iter_medias:
        info = get_video_info(v)
        bvid = info.get("bvid")
        # file_name = info.get("file_name")

        await download_v(
            bvid,
            f"{out_dir}/{collection_name}",
            credential,
            v=download_video,
        )
