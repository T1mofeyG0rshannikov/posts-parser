import asyncio
from typing import Any
from urllib.parse import urlencode

from dishka import make_async_container
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action
from sqlalchemy import URL, delete

from posts.admin.model_views.base import BaseModelView
from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.ioc.web import WebProvider
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.models import PostOrm, PostTagOrm, SitePostOrm
from posts.services.delete_post_from_sites import DeletePostFromSites
from posts.usecases.posts.deavtivate import DeactivatePost
from posts.usecases.posts.update import UpdatePost


class PostAdmin(BaseModelView, model=PostOrm):  # type: ignore
    column_list = [
        PostOrm.id,
        PostOrm.title,
        PostOrm.published,
        PostOrm.image,
        PostOrm.slug,
        PostOrm.active,
    ]

    column_searchable_list = ["title", "content"]
    list_template = "sqladmin/list-posts.html"
    details_template = "sqladmin/details-post.html"
    edit_template = "sqladmin/edit-post.html"
    form_columns = ["h1", "title", "image", "description", "content", "content2", "active", "published"]
    column_details_exclude_list = ["siteposts", "tags", "id"]

    name = "Пост"
    name_plural = "Посты"

    container = make_async_container(LoginProvider(), WebProvider(), UsecasesProvider(), DbProvider())

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

    async def on_model_delete(self, model: Any, request: Request) -> None:
        async with self.container() as request_container:
            usecase = await request_container.get(DeletePostFromSites)

            await usecase(model.id)

    async def after_model_change(self, data, model: PostOrm, is_created, request):
        if model.active:
            form = await request.form()

            request_tags_ids = [int(tag_id) for tag_id in form.get("tags", "").split(",")]

            async with self.container() as request_container:
                update_post = await request_container.get(UpdatePost)
                await update_post(post_id=model.id, new_tags_ids=request_tags_ids)
        else:
            async with self.container() as request_container:
                deactivate_post = await request_container.get(DeactivatePost)
                await deactivate_post(model.id)

    @action(name="delete_all", label="Удалить (фильтр)", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            container = make_async_container(LoginProvider(), WebProvider(), UsecasesProvider(), DbProvider())
            async with container() as request_container:
                post_data_mapper = await request_container.get(PostDataMapper)
                usecase = await request_container.get(DeletePostFromSites)
                posts = await post_data_mapper.all_ids()
                tasks = []
                for post_id in posts:
                    tasks.append(usecase(post_id))

                await asyncio.gather(*tasks)

            await session.execute(delete(SitePostOrm).where(self.filters_from_request(request)))
            await session.execute(delete(PostTagOrm).where(self.filters_from_request(request)))
            await session.execute(delete(self.model).where(self.filters_from_request(request)))
            await session.commit()
            return RedirectResponse(url="/admin/post-orm/list", status_code=303)
