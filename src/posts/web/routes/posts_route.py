from io import BytesIO
from zipfile import ZipFile

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, UploadFile

from posts.usecases.posts.avtivate import ActivatePost
from posts.usecases.posts.deavtivate import DeactivatePost
from posts.usecases.posts.parsing.parsers.zip_parser import ParsePostsFromZIP

# from posts.web.schemas.posts import ParseResponse

router = APIRouter(prefix="/posts", tags=["posts"])


async def get_zip_file(file: UploadFile) -> ZipFile:
    content = await file.read()
    return ZipFile(BytesIO(content))


@router.post("/parse", status_code=200)
@inject
async def parse_posts_handler(file: UploadFile, usecase: FromDishka[ParsePostsFromZIP]):
    zip_file = await get_zip_file(file)
    result = await usecase(zip_file)
    print(result, "result")
    return {"success": True}


@router.post("/active")
@inject
async def activate_post_handler(id: int, usecase: FromDishka[ActivatePost]):
    print(id, type(id))
    return await usecase(id)


@router.post("/deactive")
@inject
async def deactivate_post_handler(id: int, usecase: FromDishka[DeactivatePost]):
    return await usecase(id)
