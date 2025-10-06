from dishka import make_async_container

from posts.admin.auth.login_factory.interface import LoginFactory
from posts.ioc.db import DbProvider
from posts.ioc.login import LoginProvider
from posts.usecases.login import Login


class DishkaLoginFactory(LoginFactory):
    async def __call__(self) -> Login:
        container = make_async_container(LoginProvider(), DbProvider())

        async with container() as request_container:
            return await request_container.get(Login)
