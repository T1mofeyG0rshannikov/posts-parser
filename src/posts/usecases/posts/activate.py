from posts.exceptions import PostNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.posts_sender.posts_sender import PostsSender


class ActivatePost:
    def __init__(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_data_mapper: PostDataMapper,
        posts_sender: PostsSender,
        transaction: Transaction,
    ) -> None:
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
        for site in sites:
            await self._posts_sender(site=site, posts=[post])
        await self._data_mapper.save(post)
        await self._transaction.commit()
