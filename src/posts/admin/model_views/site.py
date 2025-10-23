from dishka import make_async_container
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action
from sqladmin.helpers import slugify_class_name

from posts.admin.forms import SiteCreateForm
from posts.admin.model_views.base import BaseModelView
from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.persistence.models import SiteOrm
from posts.usecases.posts.send_to_site.usecase import SendPostsToSites


class SiteAdmin(BaseModelView, model=SiteOrm):
    column_list = [SiteOrm.id, SiteOrm.username, SiteOrm.address]

    column_details_list = [SiteOrm.id, SiteOrm.username, SiteOrm.address]

    name = "Сайт Wordpress"
    name_plural = "Сайт Wordpress"

    column_default_sort = ("id", "desc")

    form = SiteCreateForm

    @action(name="synchronize", label="Синхронизировать выбранные сайты", confirmation_message="Вы уверены?")
    async def synchronize_all_action(self, request: Request):
        pks = request.query_params.get("pks")
        if pks:
            pks_list = [int(pk) for pk in pks.split(",")]

        ids = pks_list
        container = make_async_container(LoginProvider(), UsecasesProvider(), DbProvider())
        async with container() as request_container:
            usecase = await request_container.get(SendPostsToSites)

        await usecase(ids)

        return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)
