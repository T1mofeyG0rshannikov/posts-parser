from posts.exceptions import PostNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.posts_data_mapper import PostDataMapper


class ActivatePost:
    def __init__(self, posts_data_mapper: PostDataMapper, transaction: Transaction) -> None:
        self._data_mapper = posts_data_mapper
        self._transaction = transaction

    async def __call__(self, post_id: int) -> None:
        post = await self._data_mapper.get(id=post_id)
        if post is None:
            raise PostNotFoundError(f"no post with id = '{post_id}' found")
        post.active = True
        await self._data_mapper.save(post)
        await self._transaction.commit()
