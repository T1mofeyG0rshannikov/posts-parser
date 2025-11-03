import asyncio
import os

import aiofiles

from posts.services.images_loader.config import PostsImagsLoaderConfig


class PostImagesLoader:
    def __init__(self, config: PostsImagsLoaderConfig) -> None:
        self._config = config
        self._semaphore = asyncio.Semaphore(50)

    async def read_file(self, filename: str, post_ids: list[int], images_dict: dict[int, bytes]) -> None:
        post_id_string = os.path.splitext(filename)[0]
        if not post_id_string.isdigit():
            return

        post_id = int(post_id_string)
        if post_id not in post_ids:
            return

        path = os.path.join(self._config.images_dir, filename)
        async with aiofiles.open(path, "rb") as file:
            data = await file.read()

        images_dict[post_id] = data

    async def limited_read(self, filename: str, post_ids: list[int], images_dict: dict[int, bytes]) -> None:
        async with self._semaphore:
            await self.read_file(filename, post_ids, images_dict)

    async def __call__(self, post_ids: list[int]) -> dict[int, bytes]:
        files = os.listdir(self._config.images_dir)

        images_dict: dict[int, bytes] = dict()

        await asyncio.gather(*(self.limited_read(filename, post_ids, images_dict) for filename in files))
        return images_dict
