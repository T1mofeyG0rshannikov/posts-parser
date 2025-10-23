from io import BytesIO
from zipfile import ZipFile

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, UploadFile

from posts.usecases.posts.activate import ActivatePost
from posts.usecases.posts.deavtivate import DeactivatePost
from posts.usecases.posts.parse_and_send.parse_from_zip import (
    ParsePostsFromZIPAndSendToSites,
)
from posts.web.routes.base import UserAnnotation, admin_required

# from posts.web.schemas.posts import ParseResponse

router = APIRouter(prefix="/posts", tags=["posts"])


async def get_zip_file(file: UploadFile) -> ZipFile:
    content = await file.read()
    return ZipFile(BytesIO(content))


@router.post("/parse", status_code=200)
@inject
@admin_required
async def parse_posts_handler(
    file: UploadFile, user: UserAnnotation, usecase: FromDishka[ParsePostsFromZIPAndSendToSites]
):
    zip_file = await get_zip_file(file)
    return await usecase(zip_file)


@router.post("/active")
@inject
@admin_required
async def activate_post_handler(id: int, user: UserAnnotation, usecase: FromDishka[ActivatePost]):
    return await usecase(id)


@router.post("/deactive")
@inject
@admin_required
async def deactivate_post_handler(id: int, user: UserAnnotation, usecase: FromDishka[DeactivatePost]):
    return await usecase(id)
