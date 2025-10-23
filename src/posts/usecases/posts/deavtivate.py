from posts.exceptions import PostNotFoundError
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.wordpress_service.service import WordpressService


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
        site_data_mapper (SitePostDataMapper): Объект DataMapper, отвечающий за получение списка партнёрских сайтов.
        posts_data_mapper (PostDataMapper): Объект DataMapper, для работы с постами в основной базе данных.
        wordpress_service (WordpressService): Сервис, предоставляющий интерфейс для работы с WordPress REST API.
        transaction (Transaction): Объект Transaction, управляющий фиксацией изменений в базе данных.
    """

    def __init__(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_data_mapper: PostDataMapper,
        wordpress_service: WordpressService,
        transaction: Transaction,
    ) -> None:
        self._data_mapper = posts_data_mapper
        self._wordpress_service = wordpress_service
        self._site_data_mapper = site_data_mapper
        self._transaction = transaction

    async def __call__(self, post_id: int) -> None:
        post = await self._data_mapper.get(id=post_id)
        if post is None:
            raise PostNotFoundError(f"no post with id = '{post_id}' found")
        post.active = False
        await self._data_mapper.save(post)

        sites = await self._site_data_mapper.all_sites()
        for site in sites:
            wp_post = await self._wordpress_service.get_post_by_slug(site=site, slug=post.slug)
            if wp_post:
                access_token = await self._wordpress_service.get_access_token()
                await self._wordpress_service.delete_post(site=site, post_id=wp_post.id, access_token=access_token)
            else:
                print(f"no wp post with slug='{post.slug}'")

        await self._transaction.commit()
