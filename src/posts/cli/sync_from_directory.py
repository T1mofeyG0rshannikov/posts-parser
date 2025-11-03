import asyncio

from posts.di import get_container
from posts.usecases.posts.send_to_site.usecase import SendPostsToSites


async def main():
    container = await get_container()

    async with container() as request_container:
        site_ids_string = input(
            "Введите список id сайтов, которые надо синхронизировать. Оставьте пстым, если все сайты: "
        )

        site_ids = None

        if site_ids_string:
            site_ids = [int(i.strip()) for i in site_ids_string.split(",")]

        send_posts = await request_container.get(SendPostsToSites)
        print("Начало синхронизации...")
        await send_posts(site_ids=site_ids)
        print("Синхронизация окончена")


if __name__ == "__main__":
    asyncio.run(main())
