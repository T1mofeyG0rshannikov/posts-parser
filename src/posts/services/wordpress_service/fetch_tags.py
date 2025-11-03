import asyncio

from posts.dto.post import Tag
from posts.dto.site import Site
from posts.services.wordpress_service.service import WordpressService


class FetchWordpressTags:
    def __init__(self, wordpress_service: WordpressService) -> None:
        self._wordpress_service = wordpress_service
        self._lock = asyncio.Lock()

    async def _get_tags_task(self, tags: dict[str, list[Tag]], site: Site):
        new_tags = await self._wordpress_service.all_tags(site)
        async with self._lock:
            tags[site.address] = new_tags

    async def __call__(self, sites: list[Site]) -> dict[str, list[Tag]]:
        tags: dict[str, list[Tag]] = dict()
        tasks = []

        for site in sites:
            tasks.append(self._get_tags_task(tags, site))

        await asyncio.gather(*tasks)
        return tags
