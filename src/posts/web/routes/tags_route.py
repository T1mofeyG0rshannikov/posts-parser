from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from posts.usecases.tags.add_tag_to_post import AddTagToPost
from posts.usecases.tags.delete_post_tag import DeletePostTag
from posts.usecases.tags.get_all_tags import GetAllTags
from posts.web.routes.base import UserAnnotation, admin_required
from posts.web.schemas.tags import AllTagsResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/all", status_code=200, response_model=AllTagsResponse)
@inject
async def all_tags_handler(usecase: FromDishka[GetAllTags]) -> AllTagsResponse:
    tags = await usecase()
    return AllTagsResponse(tags=tags)


@router.delete("/delete-relation", status_code=200)
@admin_required
@inject
async def delete_post_tag_handler(user: UserAnnotation, tag_id: int, post_id: int, usecase: FromDishka[DeletePostTag]):
    return await usecase(tag_id=tag_id, post_id=post_id)


@router.post("/add-to-post", status_code=201)
@admin_required
@inject
async def add_tag_to_post_handler(user: UserAnnotation, tag_id: int, post_id: int, usecase: FromDishka[AddTagToPost]):
    return await usecase(tag_id=tag_id, post_id=post_id)
