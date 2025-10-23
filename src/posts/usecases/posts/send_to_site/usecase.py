import asyncio

from posts.dto.post import Tag
from posts.dto.site import Site
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.posts_sender.posts_sender import PostsSender
from posts.services.wordpress_service.service import WordpressService


class SendPostsToSites:
    def __init__(
        self,
        site_post_data_mapper: SitePostDataMapper,
        posts_sender: PostsSender,
        transaction: Transaction,
        wordpress_service: WordpressService,
    ) -> None:
        self._data_mapper = site_post_data_mapper
        self._posts_sender = posts_sender
        self._transaction = transaction
        self._wordpress_service = wordpress_service

    async def __call__(self, site_ids: list[int] | None = None):
        import time

        start = time.time()

        if site_ids is None:
            sites = await self._data_mapper.all_sites()
        else:
            sites = await self._data_mapper.filter_sites(ids=site_ids)
        print(sites, "sites")

        send_tasks = []

        wordpress_tags = []
        get_wp_tags_tasks = []

        async def get_tags(site):
            new_tags = await self._wordpress_service.all_tags(site)
            wordpress_tags.extend(new_tags)

        for site in sites:
            get_wp_tags_tasks.append(get_tags(site))

        await asyncio.gather(*get_wp_tags_tasks)

        access_token = await self._wordpress_service.get_access_token(site)

        async def send(site, posts, access_token):
            posts_sender_response = await self._posts_sender(site, posts, wordpress_tags, access_token)
            success_sended_posts_ids = posts_sender_response.success_sended_posts_ids

            await self._data_mapper.change_sended(site.id, post_ids=success_sended_posts_ids)

        for site in sites:
            posts_without_site = await self._data_mapper.filter_posts_without_site(site_id=site.id)
            posts_without_site = set(posts_without_site)
            await self._data_mapper.bulk_create_site_posts_relation(site_id=site.id, posts=posts_without_site)
            posts = await self._data_mapper.filter_posts(site_id=site.id)
            print(len(posts), len(posts_without_site), "posts")
            posts = set(posts) | posts_without_site
            # posts_sender_response = await self._posts_sender(site, posts)
            # success_sended_posts_ids = posts_sender_response.success_sended_posts_ids

            # await self._data_mapper.change_sended(site.id, post_ids=success_sended_posts_ids)
            # await self._transaction.commit()
            send_tasks.append(send(site, posts, access_token=access_token))

        await asyncio.gather(*send_tasks)
        await self._transaction.commit()
        print(time.time() - start)
