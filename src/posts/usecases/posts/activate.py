import asyncio

from posts.exceptions import PostNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.posts_sender.posts_sender import PostsSender
from posts.services.wordpress_service.service import WordpressService


class ActivatePost:
    def __init__(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_data_mapper: PostDataMapper,
        posts_sender: PostsSender,
        wordpress_service: WordpressService,
        transaction: Transaction,
    ) -> None:
        self._wordpress_service = wordpress_service
        self._data_mapper = posts_data_mapper
        self._posts_sender = posts_sender
        self._site_data_mapper = site_data_mapper
        self._transaction = transaction

    async def __call__(self, post_id: int) -> None:
        post = await self._data_mapper.get_with_tags(id=post_id)
        if post is None:
            raise PostNotFoundError(f"no post with id = '{post_id}' found")
        post.active = True

        sites = await self._site_data_mapper.all_sites()

        wordpress_tags = []
        get_wp_tags_tasks = []

        async def get_tags(site):
            new_tags = await self._wordpress_service.all_tags(site)
            wordpress_tags.extend(new_tags)

        for site in sites:
            get_wp_tags_tasks.append(get_tags(site))

        await asyncio.gather(*get_wp_tags_tasks)

        for site in sites:
            access_token = await self._wordpress_service.get_access_token(site)
            await self._posts_sender(site, posts=[post], wordpress_tags=wordpress_tags, access_token=access_token)
        await self._data_mapper.save(post)
        await self._transaction.commit()
