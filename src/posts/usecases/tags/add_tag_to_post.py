from posts.exceptions import PostAlreadyHasTagError, PostNotFoundError, TagNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.posts_data_mapper import PostDataMapper
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper


class AddTagToPost:
    def __init__(
        self, post_data_mapper: PostDataMapper, tag_data_mapper: TagDataMapper, transaction: Transaction
    ) -> None:
        self._post_data_mapper = post_data_mapper
        self._tag_data_mapper = tag_data_mapper
        self._transaction = transaction

    async def __call__(self, tag_id: int, post_id: int) -> None:
        post = await self._post_data_mapper.get(post_id)
        if post is None:
            raise PostNotFoundError(f"no post with id='{post_id}'")

        tag = await self._tag_data_mapper.get(tag_id)
        if tag is None:
            raise TagNotFoundError(f"no tag with id='{tag_id}'")

        relation = await self._tag_data_mapper.get_relation(tag_id=tag_id, post_id=post_id)

        if relation is not None:
            raise PostAlreadyHasTagError(f"post with id='{post_id}' already has tag with id='{tag_id}'")

        await self._tag_data_mapper.save_post_relation(tag_id=tag_id, post_id=post_id)
        await self._transaction.commit()
