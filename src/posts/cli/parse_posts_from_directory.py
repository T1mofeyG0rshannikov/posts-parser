import asyncio

from dishka import make_async_container

from posts.ioc.db import DbProvider
from posts.ioc.ioc import UsecasesProvider
from posts.ioc.login import LoginProvider
from posts.usecases.posts.parse_and_send.parse_from_dir import (
    ParsePostsFromDirctoryAndSendToSites,
)


async def main():
    container = make_async_container(LoginProvider(), UsecasesProvider(), DbProvider())

    async with container() as request_container:
        parse_posts = await request_container.get(ParsePostsFromDirctoryAndSendToSites)
        print("Начало парсинга...")
        parse_response = await parse_posts()
        print(f"Пропущено постов (дубликаты): {parse_response.skipped}")
        print(f"Добавлено постов: {parse_response.inserted}")
        print(f"Неправильных постов: {parse_response.invalid}")


if __name__ == "__main__":
    asyncio.run(main())
