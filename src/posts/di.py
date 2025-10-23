from functools import lru_cache

from dishka import make_container
from fastapi import FastAPI

from posts.ioc.db import DbProvider
from posts.ioc.ioc import AppProvider, UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.ioc.web import WebProvider


@lru_cache
def get_container(app: FastAPI = None):
    return make_container(
        AppProvider(), UsecasesProvider(), DbProvider(), WebProvider(), LoginProvider(), context={FastAPI: app}
    )
