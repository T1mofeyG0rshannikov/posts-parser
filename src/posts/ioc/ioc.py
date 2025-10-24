from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, from_context, provide
from fastapi import FastAPI
from redis import Redis  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from posts.admin.admin import CustomAdmin
from posts.admin.auth.backend import AdminAuth
from posts.admin.auth.login_factory.dishka_login_factory import DishkaLoginFactory
from posts.admin.config import AdminConfig
from posts.persistence.data_mappers.error_log_data_mapper import ErrorLogDataMapper
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.persistence.data_mappers.site_post_data_mapper import SitePostDataMapper
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.persistence.data_mappers.user_data_mapper import UserDataMapper
from posts.persistence.redis_config import RedisConfig
from posts.services.delete_post_from_sites import DeletePostFromSites
from posts.services.images_loader.config import PostsImagsLoaderConfig
from posts.services.images_loader.images_loader import PostImagesLoader
from posts.services.logger import DbLogger
from posts.services.posts_sender.posts_sender import PostsSender
from posts.services.posts_sender.send_single_post import SendSinglePostToSite
from posts.services.wordpress_service.service import WordpressService
from posts.usecases.create_user import CreateUser
from posts.usecases.posts.activate import ActivatePost
from posts.usecases.posts.deavtivate import DeactivatePost
from posts.usecases.posts.parse_and_send.base import ParsePostsAndSendToSites
from posts.usecases.posts.parse_and_send.parse_from_dir import (
    ParsePostsFromDirctoryAndSendToSites,
)
from posts.usecases.posts.parse_and_send.parse_from_zip import (
    ParsePostsFromZIPAndSendToSites,
)
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.db_writer_worker import DbWriterWorker
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.config import (
    DirectoryDiscovererConfig,
)
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.directory_discoverer import (
    DirectoryDiscoverer,
)
from posts.usecases.posts.parsing.parsers.directory_parser import (
    ParsePostsFromDirectory,
)
from posts.usecases.posts.parsing.parsers.zip_parser import ParsePostsFromZIP
from posts.usecases.posts.persist_posts import PersistPosts
from posts.usecases.posts.send_to_site.adapter import WordpressPostAdapter
from posts.usecases.posts.send_to_site.usecase import SendPostsToSites
from posts.usecases.tags.add_tag_to_post import AddTagToPost
from posts.usecases.tags.delete_post_tag import DeletePostTag
from posts.usecases.tags.get_all_tags import GetAllTags
from posts.user.auth.jwt_processor import JwtProcessor
from posts.user.password_hasher import PasswordHasher


class UsecasesProvider(Provider):
    @provide(scope=Scope.APP)
    def get_directory_discoverer_config(self) -> DirectoryDiscovererConfig:
        return DirectoryDiscovererConfig()

    @provide(scope=Scope.APP)
    def get_admin_config(self) -> AdminConfig:
        return AdminConfig()

    @provide(scope=Scope.APP)
    def get_parse_config(self) -> ParseConfig:
        return ParseConfig()

    @provide(scope=Scope.APP)
    def get_directory_discoverer(
        self, directory_discoverer_config: DirectoryDiscovererConfig, parse_config: ParseConfig
    ) -> DirectoryDiscoverer:
        return DirectoryDiscoverer(config=directory_discoverer_config, n_parser_workers=parse_config.N_PARSER_WORKERS)

    @provide(scope=Scope.SESSION)
    def get_db_logger(self, error_log_data_mapper: ErrorLogDataMapper, session_maker: async_sessionmaker) -> DbLogger:
        return DbLogger(error_log_data_mapper=error_log_data_mapper, session_maker=session_maker)

    @provide(scope=Scope.SESSION)
    def get_parse_posts_from_directory_interactor(
        self,
        parse_config: ParseConfig,
        tag_data_mapper: TagDataMapper,
        directory_discoverer: DirectoryDiscoverer,
        transaction: AsyncSession,
        db_worker: DbWriterWorker,
        logger: DbLogger,
    ) -> ParsePostsFromDirectory:
        return ParsePostsFromDirectory(
            config=parse_config,
            tag_data_mapper=tag_data_mapper,
            directory_discoverer=directory_discoverer,
            transaction=transaction,
            db_worker=db_worker,
            logger=logger,
        )

    @provide(scope=Scope.REQUEST)
    def get_parse_from_directory_and_send_posts(
        self, parse_posts: ParsePostsFromDirectory, send_posts_to_sites: SendPostsToSites
    ) -> ParsePostsFromDirctoryAndSendToSites:
        return ParsePostsFromDirctoryAndSendToSites(parse_posts=parse_posts, send_posts=send_posts_to_sites)

    @provide(scope=Scope.REQUEST)
    async def get_parse_from_zip_and_send_posts(
        self, parse_posts: ParsePostsFromZIP, send_posts_to_sites: SendPostsToSites
    ) -> ParsePostsFromZIPAndSendToSites:
        return ParsePostsFromZIPAndSendToSites(parse_posts=parse_posts, send_posts=send_posts_to_sites)

    @provide(scope=Scope.SESSION)
    async def get_create_user(
        self, session: AsyncSession, user_data_mapper: UserDataMapper, password_hasher: PasswordHasher
    ) -> CreateUser:
        return CreateUser(user_data_mapper=user_data_mapper, password_hasher=password_hasher, transaction=session)

    @provide(scope=Scope.APP)
    def get_images_loadr_config(self) -> PostsImagsLoaderConfig:
        return PostsImagsLoaderConfig()

    @provide(scope=Scope.REQUEST)
    async def get_images_loader(self, config: PostsImagsLoaderConfig) -> PostImagesLoader:
        return PostImagesLoader(config=config)

    @provide(scope=Scope.REQUEST)
    async def get_posts_sender(
        self,
        wordpress_service: WordpressService,
        logger: DbLogger,
        images_loader: PostImagesLoader,
        send_single_post: SendSinglePostToSite,
    ) -> PostsSender:
        return PostsSender(
            images_loader=images_loader,
            send_single_post=send_single_post,
            logger=logger,
            wordpress_service=wordpress_service,
        )

    @provide(scope=Scope.REQUEST)
    def get_activate_post(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_sender: PostsSender,
        posts_data_mapper: PostDataMapper,
        wordpress_service: WordpressService,
        session: AsyncSession,
    ) -> ActivatePost:
        return ActivatePost(
            wordpress_service=wordpress_service,
            posts_data_mapper=posts_data_mapper,
            transaction=session,
            site_data_mapper=site_data_mapper,
            posts_sender=posts_sender,
        )

    @provide(scope=Scope.REQUEST)
    def get_deactivate_post(
        self,
        delete_post_from_sites: DeletePostFromSites,
        posts_data_mapper: PostDataMapper,
        session: AsyncSession,
    ) -> DeactivatePost:
        return DeactivatePost(
            posts_data_mapper=posts_data_mapper,
            delete_post_from_sites=delete_post_from_sites,
            transaction=session,
        )

    @provide(scope=Scope.SESSION)
    def get_persist_posts(self, post_data_mapper: PostDataMapper, tag_data_mapper: TagDataMapper) -> PersistPosts:
        return PersistPosts(post_data_mapper=post_data_mapper, tag_data_mapper=tag_data_mapper)

    @provide(scope=Scope.SESSION)
    def get_db_worker(
        self, post_data_mapper: PostDataMapper, config: ParseConfig, persist_posts: PersistPosts
    ) -> DbWriterWorker:
        return DbWriterWorker(post_data_mapper=post_data_mapper, config=config, persist_posts=persist_posts)

    @provide(scope=Scope.REQUEST)
    def get_all_tags(self, tag_data_mapper: TagDataMapper) -> GetAllTags:
        return GetAllTags(tag_data_mapper=tag_data_mapper)

    @provide(scope=Scope.REQUEST)
    def get_delete_post_tag(
        self, post_data_mapper: PostDataMapper, tag_data_mapper: TagDataMapper, transaction: AsyncSession
    ) -> DeletePostTag:
        return DeletePostTag(
            post_data_mapper=post_data_mapper, tag_data_mapper=tag_data_mapper, transaction=transaction
        )

    @provide(scope=Scope.REQUEST)
    def get_add_tag_to_post(
        self, post_data_mapper: PostDataMapper, tag_data_mapper: TagDataMapper, transaction: AsyncSession
    ) -> AddTagToPost:
        return AddTagToPost(post_data_mapper=post_data_mapper, tag_data_mapper=tag_data_mapper, transaction=transaction)

    @provide(scope=Scope.APP)
    def get_wordpress_post_adapter(self) -> WordpressPostAdapter:
        return WordpressPostAdapter()

    @provide(scope=Scope.REQUEST)
    async def get_https_session(self) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(timeout=60) as session:
            yield session

    @provide(scope=Scope.APP)
    def get_redis_config(self) -> RedisConfig:
        return RedisConfig()

    @provide(scope=Scope.APP)
    def get_redis(self, config: RedisConfig) -> Redis:
        return Redis(host=config.host, port=config.port, db=config.db, decode_responses=True)

    @provide(scope=Scope.REQUEST)
    def get_wordpress_service(self, session: httpx.AsyncClient, redis: Redis) -> WordpressService:
        return WordpressService(session=session, redis=redis)

    @provide(scope=Scope.REQUEST)
    def get_send_single_post(
        self, wordpress_service: WordpressService, adapter: WordpressPostAdapter, logger: DbLogger
    ) -> SendSinglePostToSite:
        return SendSinglePostToSite(wordpress_service=wordpress_service, adapter=adapter, logger=logger)

    @provide(scope=Scope.REQUEST)
    def get_delete_post_from_sites(
        self,
        site_data_mapper: SitePostDataMapper,
        posts_data_mapper: PostDataMapper,
        wordpress_service: WordpressService,
    ) -> DeletePostFromSites:
        return DeletePostFromSites(
            site_data_mapper=site_data_mapper, posts_data_mapper=posts_data_mapper, wordpress_service=wordpress_service
        )

    @provide(scope=Scope.REQUEST)
    def get_send_posts_to_sites(
        self,
        wordpress_service: WordpressService,
        site_post_data_mapper: SitePostDataMapper,
        posts_sender: PostsSender,
        transaction: AsyncSession,
    ) -> SendPostsToSites:
        return SendPostsToSites(
            site_post_data_mapper=site_post_data_mapper,
            wordpress_service=wordpress_service,
            posts_sender=posts_sender,
            transaction=transaction,
        )


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def get_login_factory(self) -> DishkaLoginFactory:
        return DishkaLoginFactory()

    @provide(scope=Scope.APP)
    def get_authentication_backend(
        self,
        jwt_processor: JwtProcessor,
        password_hasher: PasswordHasher,
        admin_config: AdminConfig,
        login_factory: DishkaLoginFactory,
    ) -> AdminAuth:
        return AdminAuth(
            jwt_processor=jwt_processor,
            password_hasher=password_hasher,
            config=admin_config,
            login_factory=login_factory,
        )

    app = from_context(FastAPI, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_custom_admin(
        self, app: FastAPI, engine: AsyncEngine, authentication_backend: AdminAuth, admin_config: AdminConfig
    ) -> CustomAdmin:
        return CustomAdmin(
            app=app,
            engine=engine,
            authentication_backend=authentication_backend,
            templates_dir=admin_config.templates_dir,
        )
