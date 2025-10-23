import asyncio

from posts.dto.post import PostWithTags, Tag
from posts.dto.posts_sender import PostsSenderResponse
from posts.dto.site import Site
from posts.interfaces.logger import Logger
from posts.services.images_loader.images_loader import PostImagesLoader
from posts.services.posts_sender.send_single_post import SendSinglePostToSite
from posts.services.wordpress_service.service import WordpressService


class PostsSender:
    """
    Отправляет список постов на указанный WordPress-сайт.

    Класс выполняет следющую задачу:
      - загружает изображения для переданных постов;
      - вызывает SendSinglePostToSite для каждого поста;
      - собирает результаты и возвращает PostsSenderResponse.

    Используется внутри юзкейсов, отвечающих за массовую отправку постов постов.

    Параметры:
        - images_loader (Po): асинхронный сервис, который по списку id возвращает dict {id: bytes}.
        - send_single_post: сервис, отправляющий один пост на сайт.

    """

    def __init__(
        self,
        images_loader: PostImagesLoader,
        send_single_post: SendSinglePostToSite,
        logger: Logger,
        wordpress_service: WordpressService,
    ) -> None:
        self._images_loader = images_loader
        self._send_single_post = send_single_post
        self._logger = logger
        self._wordpress_service = wordpress_service

    async def __call__(
        self, site: Site, posts: list[PostWithTags], wordpress_tags: list[Tag], access_token: str
    ) -> PostsSenderResponse:
        post_ids = [post.id for post in posts]

        images_dict = await self._images_loader(post_ids)

        success_sended_posts_ids = []
        error_sended_posts_ids = []

        tasks = []

        send_tags_tasks = []

        async def send_tag(site, tag, access_token):
            tag_response = await self._wordpress_service.send_tag(site, tag, access_token=access_token)
            if tag_response.success:
                wordpress_tags.append(tag_response.data)
            else:
                await self._logger.log(
                    title=f"Ошибка при отправлении тэга с id='{tag.id}' на сайт '{site.address}'",
                    message=tag_response.error_message,
                )

        for post in posts:
            for tag in post.tags:
                if tag not in wordpress_tags:
                    send_tags_tasks.append(send_tag(site, tag, access_token=access_token))

        await asyncio.gather(*send_tags_tasks)

        async def send(site, post, post_image):
            response = await self._send_single_post(
                site=site, post=post, image=post_image, wordpress_tags=wordpress_tags, access_token=access_token
            )
            if response.success:
                success_sended_posts_ids.append(post.id)
            else:
                error_sended_posts_ids.append(post.id)

        for post in posts:
            post_image = images_dict.get(post.id)
            tasks.append(send(site, post, post_image))

        await asyncio.gather(*tasks)

        return PostsSenderResponse(
            success_sended_posts_ids=success_sended_posts_ids, error_sended_posts_ids=error_sended_posts_ids
        )
