from posts.dto.operation_result import BaseOperationResult
from posts.dto.post import PostWithTags, Tag
from posts.dto.site import Site
from posts.interfaces.logger import Logger
from posts.services.wordpress_service.service import WordpressService
from posts.usecases.posts.send_to_site.adapter import WordpressPostAdapter


class SendSinglePostToSite:
    """
    Отправляет один пост на указанный WordPress сайт.

    Класс отвечает за подготовку и передачу одного объекта PostWithTags в формат,
    понятный WordPress API.

    Параметры:
        post_data_mapper (PostDataMapper): Маппер, отвечающий за сохранение постов в БД.
        tag_data_mapper (TagDataMapper): Маппер, отвечающий за сохранение тегов и связей пост–тег.
        wordpress_service (WordpressService): посредник для вызовов к WordPress API.
        adapter (WordpressPostAdaper): адаптер, который преобразует PostWithTags -> WordpressPostDTO.
        logger (Logger): интерфейс логирования.
    """

    def __init__(self, wordpress_service: WordpressService, adapter: WordpressPostAdapter, logger: Logger) -> None:
        self._wordpress_service = wordpress_service
        self._adapter = adapter
        self._logger = logger

    async def __call__(
        self, site: Site, post: PostWithTags, wordpress_tags: list[Tag], access_token: str, image: bytes | None = None
    ) -> BaseOperationResult:
        if image is not None:
            image_name = f"{post.id}.jpg"

            featured_media = await self._wordpress_service.send_post_image(
                site, image_name, image, access_token=access_token
            )
        else:
            featured_media = None

        wordpress_post = self._adapter.execute(post=post, wp_tags=wordpress_tags, featured_media=featured_media)
        response = await self._wordpress_service.send_post(post=wordpress_post, site=site, access_token=access_token)
        if response.success:
            return BaseOperationResult(success=True)
        else:
            await self._logger.log(
                title=f"Ошибка при отправлении поста с id='{post.id}' на сайт '{site.address}'",
                message=response.error_message,
            )
            return BaseOperationResult(success=False)
