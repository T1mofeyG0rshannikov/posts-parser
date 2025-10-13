import asyncio

from dishka import make_async_container

from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.usecases.posts.parsing.parsers.directory_parser import (
    ParsePostsFromDirectory,
)


async def main():
    container = make_async_container(LoginProvider(), UsecasesProvider(), DbProvider())

    async with container() as request_container:
        parse_posts = await request_container.get(ParsePostsFromDirectory)
        print("Начало парсинга...")
        parse_response = await parse_posts()
        print(f"Пропущено постов (дубликаты): {parse_response.skipped}")
        print(f"Добавлено постов: {parse_response.inserted}")


if __name__ == "__main__":
    asyncio.run(main())
