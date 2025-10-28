import asyncio

from posts.dto.post import PostWithTags, Tag
from posts.dto.site import Site
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.get_site_access_token import GetSiteAccessToken
from posts.services.posts_sender.posts_sender import PostsSender
from posts.services.wordpress_service.fetch_tags import FetchWordpressTags


class SendPostsToSites:
    def __init__(
        self,
        site_post_data_mapper: SitePostDataMapper,
        posts_sender: PostsSender,
        transaction: Transaction,
        fetch_wordpress_tags: FetchWordpressTags,
        get_site_access_token: GetSiteAccessToken,
    ) -> None:
        self._get_site_access_token = get_site_access_token
        self._data_mapper = site_post_data_mapper
        self._posts_sender = posts_sender
        self._transaction = transaction
        self._fetch_wordpress_tags = fetch_wordpress_tags

    async def _send_task(
        self, site: Site, posts: list[PostWithTags], access_token: str, wordpress_tags: list[Tag]
    ) -> None:
        posts_sender_response = await self._posts_sender(site, posts, wordpress_tags, access_token)
        success_sended_posts_ids = posts_sender_response.success_sended_posts_ids

        await self._data_mapper.change_sended(site.id, post_ids=success_sended_posts_ids)

    async def __call__(self, site_ids: list[int] | None = None):
        import time

        start = time.time()

        if site_ids is None:
            sites = await self._data_mapper.all_sites()
        else:
            sites = await self._data_mapper.filter_sites(ids=site_ids)
        print(sites, "sites")

        send_tasks = []

        wordpress_tags = await self._fetch_wordpress_tags(sites)

        access_tokens = dict()
        for site in sites:
            access_token = await self._get_site_access_token(site)
            access_tokens[site.address] = access_token

        for site in sites:
            posts_without_site = await self._data_mapper.filter_posts_without_site(site_id=site.id)

            await self._data_mapper.bulk_create_site_posts_relation(site_id=site.id, posts=posts_without_site)
            posts = await self._data_mapper.filter_posts(site_id=site.id)
            print(len(posts), len(posts_without_site), "posts")
            print([post.id for post in posts], "pppp")
            print([post.id for post in posts_without_site], "zzzz")
            posts = set(posts) | set(posts_without_site)
            print(len(posts), "posts")

            send_tasks.append(
                self._send_task(
                    site, posts, access_token=access_tokens[site.address], wordpress_tags=wordpress_tags[site.address]
                )
            )

        await asyncio.gather(*send_tasks)
        await self._transaction.commit()
        print(time.time() - start, "time sended")
