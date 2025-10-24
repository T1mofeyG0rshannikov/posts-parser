from posts.exceptions import PostNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.services.delete_post_from_sites import DeletePostFromSites


class DeactivatePost:
    """
    Класс, предназначенный для деактивации поста во внутренней системе и удаления его
    со всех партнёрских WordPress-сайтов.

    Класс помечает пост как неактивный в базе данных
    и синхронизирует это состояние с внешними системами, удаляя соответствующие посты
    с каждого подключённого WordPress-сайта.
    Для обеспечения консистентности данных используется транзакция, которая фиксируется
    только после успешного удаления постов со всех сайтов.

    Args:
        posts_data_mapper (PostDataMapper): Объект DataMapper, для работы с постами в основной базе данных.
        delete_post_from_sites (DeletePostFromSites): Сервис, который удаляет указанный пост со всех привязанных WOrdpress сайтов.
        transaction (Transaction): Объект Transaction, управляющий фиксацией изменений в базе данных.
    """

    def __init__(
        self, posts_data_mapper: PostDataMapper, transaction: Transaction, delete_post_from_sites: DeletePostFromSites
    ) -> None:
        self._data_mapper = posts_data_mapper
        self._transaction = transaction
        self._delete_post_from_sites = delete_post_from_sites

    async def __call__(self, post_id: int) -> None:
        post = await self._data_mapper.get(id=post_id)
        if post is None:
            raise PostNotFoundError(f"no post with id = '{post_id}' found")
        post.active = False
        await self._data_mapper.save(post)

        await self._delete_post_from_sites(post_id=post.id)

        await self._transaction.commit()
