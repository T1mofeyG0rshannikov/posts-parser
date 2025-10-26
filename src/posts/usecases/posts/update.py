from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.services.delete_post_from_sites import DeletePostFromSites
from posts.services.get_site_access_token import GetSiteAccessToken
from posts.services.posts_sender.posts_sender import PostsSender
from posts.services.wordpress_service.fetch_tags import FetchWordpressTags


class UpdatePost:
    def __init__(
        self,
        post_data_mapper: PostDataMapper,
        tag_data_mapper: TagDataMapper,
        posts_sender: PostsSender,
        site_data_mapper: SitePostDataMapper,
        get_site_access_token: GetSiteAccessToken,
        fetch_wordpress_tags: FetchWordpressTags,
        delete_post_from_sites: DeletePostFromSites,
        transaction: Transaction,
    ) -> None:
        self._get_site_access_token = get_site_access_token
        self._fetch_wordpress_tags = fetch_wordpress_tags
        self._site_data_mapper = site_data_mapper
        self._post_data_mapper = post_data_mapper
        self._tag_data_mapper = tag_data_mapper
        self._posts_sender = posts_sender
        self._delete_post_from_sites = delete_post_from_sites
        self._transaction = transaction

    async def __call__(self, post_id: int, new_tags_ids: list[int]) -> None:
        post_tags = await self._tag_data_mapper.filter(post_id=post_id)
        post_tags_ids = [tag.id for tag in post_tags]

        for new_tag_id in new_tags_ids:
            if new_tag_id not in post_tags_ids:
                await self._tag_data_mapper.save_post_relation(tag_id=new_tag_id, post_id=post_id)

        for post_tag_id in post_tags_ids:
            if post_tag_id not in new_tags_ids:
                await self._tag_data_mapper.delete_post_tag_relation(tag_id=post_tag_id, post_id=post_id)

        await self._transaction.commit()

        updated_post = await self._post_data_mapper.get_with_tags(id=post_id)

        sites = await self._site_data_mapper.all_sites()

        wordpress_tags = await self._fetch_wordpress_tags(sites)

        for site in sites:
            access_token = await self._get_site_access_token(site)
            await self._delete_post_from_sites(post_id=post_id)
            await self._posts_sender(
                site=site, posts=[updated_post], access_token=access_token, wordpress_tags=wordpress_tags[site.address]
            )
