import asyncio

from dishka import make_async_container, make_container

from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.usecases.posts.parsing.parsers.base import ParsePosts


async def main():
    container = make_async_container(LoginProvider(), UsecasesProvider(), DbProvider())

    async with container() as request_container:
        parse_posts = await request_container.get(ParsePosts)

        await parse_posts()


if __name__ == "__main__":
    asyncio.run(main())
