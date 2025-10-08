from typing import Any
from urllib.parse import urlencode

from fastapi import Request
from sqlalchemy import URL

from posts.admin.model_views.base import BaseModelView
from posts.persistence.data_mappers.posts_data_mapper import PostDataMapper
from posts.persistence.models import PostOrm


class PostAdmin(BaseModelView, model=PostOrm):  # type: ignore
    column_list = [
        PostOrm.id,
        PostOrm.title,
        PostOrm.published,
        PostOrm.slug,
        PostOrm.active,
    ]

    list_template = "sqladmin/list-posts.html"
    details_template = "sqladmin/details-post.html"
    edit_template = "sqladmin/edit-post.html"
    form_columns = ["h1", "title", "description", "content", "content2", "active", "published"]
    column_details_exclude_list = ["tags", "id"]
    name = "Пост"
    name_plural = "Посты"

    def get_object_identifier(self, obj):
        return obj.id

    def _build_url_for(self, name: str, request: Request, obj: Any) -> URL:
        return request.url_for(
            name,
            identity="post-orm",
            pk=obj.id,
        )

    def _url_for_delete(self, request: Request, obj: Any) -> str:
        query_params = urlencode({"pks": obj.id})
        url = request.url_for("admin:delete", identity="post-orm")
        return str(url) + "?" + query_params

    async def get_object_for_details(self, value: Any) -> Any:
        async with self.session_maker() as session:
            data_mapper = PostDataMapper(session)

            return await data_mapper.get_with_tags(id=int(value))

    async def get_object_for_edit(self, request: Request) -> Any:
        async with self.session_maker() as session:
            data_mapper = PostDataMapper(session)

            return await data_mapper.get_with_tags(id=int(request.path_params["pk"]))
