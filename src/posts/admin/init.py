from dishka import make_container
from fastapi import FastAPI

from posts.admin.admin import CustomAdmin
from posts.admin.model_views.error_log import ErrorLogAdmin
from posts.admin.model_views.post import PostAdmin
from posts.admin.model_views.tag import TagAdmin
from posts.ioc.db import DbProvider
from posts.ioc.ioc import AppProvider, UsecasesProvider
from posts.ioc.login import LoginProvider


def init_admin(app: FastAPI) -> None:
    container = make_container(AppProvider(), UsecasesProvider(), DbProvider(), LoginProvider(), context={FastAPI: app})
    admin = container.get(CustomAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(ErrorLogAdmin)
