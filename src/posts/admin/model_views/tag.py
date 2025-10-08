from typing import Any
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action
from sqlalchemy import URL, delete

from posts.admin.model_views.base import BaseModelView
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.persistence.models import PostTagOrm, TagOrm


class TagAdmin(BaseModelView, model=TagOrm):  # type: ignore
    column_list = [TagOrm.id, TagOrm.name, TagOrm.slug]

    details_template = "sqladmin/details-tag.html"
    name = "Тег"
    name_plural = "Теги"
    column_details_exclude_list = ["posts", "id"]
    form_excluded_columns = ["posts"]

    @action(name="delete_all", label="Удалить (фильтр)", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(PostTagOrm).where(self.filters_from_request(request)))
            await session.execute(delete(self.model).where(self.filters_from_request(request)))
            await session.commit()
            return RedirectResponse(url="/admin/tag-orm/list", status_code=303)

    def get_object_identifier(self, obj):
        return obj.id

    def _build_url_for(self, name: str, request: Request, obj: Any) -> URL:
        return request.url_for(
            name,
            identity="tag-orm",
            pk=obj.id,
        )

    def _url_for_delete(self, request: Request, obj: Any) -> str:
        query_params = urlencode({"pks": obj.id})
        url = request.url_for("admin:delete", identity="tag-orm")
        return str(url) + "?" + query_params

    async def get_object_for_details(self, value: Any) -> Any:
        async with self.session_maker() as session:
            data_mapper = TagDataMapper(session)

            return await data_mapper.get_with_posts(id=int(value))

    async def get_object_for_edit(self, request: Request) -> Any:
        async with self.session_maker() as session:
            data_mapper = TagDataMapper(session)

            return await data_mapper.get_with_posts(id=int(request.path_params["pk"]))
