from dishka import make_async_container
from dishka.integrations import fastapi as fastapi_integration
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from posts.admin.config import AdminConfig
from posts.admin.init import init_admin
from posts.di import get_sync_container
from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.ioc.web import WebProvider
from posts.web.exc_handler import init_exc_handlers
from posts.web.routes.posts_route import router as posts_router
from posts.web.routes.tags_route import router as tags_router

app = FastAPI()

container = get_sync_container(app)
admin_config = container.get(AdminConfig)

app.add_middleware(SessionMiddleware, secret_key=admin_config.secret_key)
app.include_router(router=posts_router)
app.include_router(router=tags_router)
init_admin(app)
init_exc_handlers(app)

container2 = make_async_container(UsecasesProvider(), DbProvider(), LoginProvider(), WebProvider())
fastapi_integration.setup_dishka(container2, app)
