from posts.exceptions import PostNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.get_site_access_token import GetSiteAccessToken
from posts.services.posts_sender.posts_sender import PostsSender
from posts.services.wordpress_service.fetch_tags import FetchWordpressTags


class ActivatePost:
    def __init__(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_data_mapper: PostDataMapper,
        posts_sender: PostsSender,
        get_site_access_token: GetSiteAccessToken,
        fetch_wordpress_tags: FetchWordpressTags,
        transaction: Transaction,
    ) -> None:
        self._get_site_access_token = get_site_access_token
        self._data_mapper = posts_data_mapper
        self._posts_sender = posts_sender
        self._site_data_mapper = site_data_mapper
        self._fetch_wordpress_tags = fetch_wordpress_tags
        self._transaction = transaction

    async def __call__(self, post_id: int) -> None:
        post = await self._data_mapper.get_with_tags(id=post_id)
        if post is None:
            raise PostNotFoundError(f"no post with id = '{post_id}' found")
        post.active = True

        sites = await self._site_data_mapper.all_sites()

        wordpress_tags = await self._fetch_wordpress_tags(sites)

        for site in sites:
            access_token = await self._get_site_access_token(site)
            await self._posts_sender(
                site, posts=[post], wordpress_tags=wordpress_tags[site.address], access_token=access_token
            )

        await self._data_mapper.save(post)
        await self._transaction.commit()
