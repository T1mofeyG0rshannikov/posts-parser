from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.get_site_access_token import GetSiteAccessToken
from posts.services.wordpress_service.service import WordpressService


class DeletePostFromSites:
    def __init__(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_data_mapper: PostDataMapper,
        wordpress_service: WordpressService,
        get_site_access_token: GetSiteAccessToken,
    ) -> None:
        self._data_mapper = posts_data_mapper
        self._wordpress_service = wordpress_service
        self._site_data_mapper = site_data_mapper
        self._get_site_access_token = get_site_access_token

    async def __call__(self, post_id: int):
        post = await self._data_mapper.get(post_id)

        sites = await self._site_data_mapper.all_sites()
        for site in sites:
            wp_post = await self._wordpress_service.get_post_by_slug(site=site, post=post)
            if wp_post:
                access_token = await self._get_site_access_token(site)
                await self._wordpress_service.delete_post(site=site, post_id=wp_post.id, access_token=access_token)
            else:
                print(f"no wp post with slug='{post.slug}'")
