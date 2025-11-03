import asyncio
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from posts.dto.post import PostWithTags, Tag
from posts.dto.posts_sender import PostsSenderResponse
from posts.dto.site import Site
from posts.interfaces.logger import Logger
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.services.images_loader.images_loader import PostImagesLoader
from posts.services.posts_sender.send_single_post import SendSinglePostToSite
from posts.services.wordpress_service.service import WordpressService


class PostsSender:
    """
    Отправляет список постов на указанный WordPress-сайт и сохраняет в бд статус отправленных постов

    Класс выполняет следющую задачу:
      - загружает изображения для переданных постов;
      - вызывает SendSinglePostToSite для каждого поста;
      - собирает результаты и возвращает PostsSenderResponse.

    Используется внутри юзкейсов, отвечающих за массовую отправку постов постов.

    Параметры:
        - images_loader (PostImagesLoader): асинхронный сервис, который по списку id возвращает dict {id: bytes}.
        - send_single_post (SendSinglePostToSite): сервис, отправляющий один пост на сайт.
        - logger (Logger): логер ошибок
        - wordpress_service (WordpressService): - сервис для работы с WordPress RestAPI
        - transaction (Transaction): - транзакция базы данных
    """

    def __init__(
        self,
        images_loader: PostImagesLoader,
        send_single_post: SendSinglePostToSite,
        logger: Logger,
        wordpress_service: WordpressService,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> None:
        self._images_loader = images_loader
        self._send_single_post = send_single_post
        self._logger = logger
        self._wordpress_service = wordpress_service
        self._batch_size = 50
        self._session_maker = session_maker
        self._lock = asyncio.Lock()

    @staticmethod
    @lru_cache
    def get_semaphore(site: Site) -> asyncio.Semaphore:
        return asyncio.Semaphore(value=site.max_connections_limit)

    async def send_tag_task(self, site: Site, tag: Tag, access_token: str, wordpress_tags: list[Tag]) -> None:
        async with self.get_semaphore(site):
            tag_response = await self._wordpress_service.send_tag(site, tag, access_token=access_token)
            if tag_response.success:
                async with self._lock:
                    wordpress_tags.append(tag_response.data)
            else:
                await self._logger.log(
                    title=f"Ошибка при отправлении тэга с id='{tag.id}' на сайт '{site.address}'",
                    message=tag_response.error_message,
                )

    async def send_post_task(
        self,
        post: PostWithTags,
        site: Site,
        error_sended_posts_ids: list[int],
        post_image: bytes,
        access_token: str,
        success_sended_posts_ids: list[int],
        wordpress_tags: list[Tag],
    ) -> None:
        async with self.get_semaphore(site):
            response = await self._send_single_post(
                site=site, post=post, image=post_image, wordpress_tags=wordpress_tags, access_token=access_token
            )
            async with self._lock:
                if response.success:
                    success_sended_posts_ids.append(post.id)
                else:
                    error_sended_posts_ids.append(post.id)

    async def send_posts_batch(
        self,
        batch_posts: list[PostWithTags],
        images_dict: dict[str, bytes],
        site: Site,
        wordpress_tags: list[Tag],
        access_token: str,
    ):
        """
        Метод, который отправляет батч постов на сайт и фиксирует успешные отправки
        в состоянии бд, для лучшей констистентности данных, чтоб не зависеть от результата
        выполнения отправки других батчей
        """

        success_sended_posts_ids: list[int] = []
        error_sended_posts_ids: list[int] = []

        tasks = []

        for post in batch_posts:
            post_image = images_dict.get(post.id)
            tasks.append(
                self.send_post_task(
                    post=post,
                    site=site,
                    success_sended_posts_ids=success_sended_posts_ids,
                    error_sended_posts_ids=error_sended_posts_ids,
                    post_image=post_image,
                    access_token=access_token,
                    wordpress_tags=wordpress_tags,
                )
            )

        await asyncio.gather(*tasks)
        async with self._session_maker() as session:
            data_mapper = SitePostDataMapper(session=session)
            print(success_sended_posts_ids, "ids")
            await data_mapper.change_sended(site.id, post_ids=success_sended_posts_ids)
            await session.commit()

    async def __call__(
        self, site: Site, posts: list[PostWithTags], wordpress_tags: list[Tag], access_token: str
    ) -> PostsSenderResponse:
        for i in range(0, len(posts), self._batch_size):
            batch_posts = posts[i : i + self._batch_size]
            print(len(batch_posts), "batched_posts")

            send_tags_tasks = []

            for post in batch_posts:
                for tag in post.tags:
                    if tag not in wordpress_tags:
                        send_tags_tasks.append(
                            self.send_tag_task(site, tag, access_token=access_token, wordpress_tags=wordpress_tags)
                        )

            print("start send tags")
            await asyncio.gather(*send_tags_tasks)
            print("sended tags")

            post_ids = [post.id for post in batch_posts]
            print("getting images")
            images_dict = await self._images_loader(post_ids)
            print("successfully load images")

            await self.send_posts_batch(
                batch_posts=batch_posts,
                images_dict=images_dict,
                site=site,
                access_token=access_token,
                wordpress_tags=wordpress_tags,
            )

        return PostsSenderResponse(success_sended_posts_ids=[], error_sended_posts_ids=[])
