from dishka import Provider, Scope, from_context, provide
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from posts.admin.admin import CustomAdmin
from posts.admin.auth.backend import AdminAuth
from posts.admin.auth.login_factory.dishka_login_factory import DishkaLoginFactory
from posts.admin.config import AdminConfig
from posts.persistence.data_mappers.posts_data_mapper import PostDataMapper
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.persistence.data_mappers.user_data_mapper import UserDataMapper
from posts.usecases.create_user import CreateUser
from posts.usecases.posts.avtivate import ActivatePost
from posts.usecases.posts.deavtivate import DeactivatePost
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
from posts.usecases.posts.persist_posts import PersistPosts
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
    def get_parse_posts_from_directory_interactor(
        self,
        parse_config: ParseConfig,
        tag_data_mapper: TagDataMapper,
        directory_discoverer: DirectoryDiscoverer,
        transaction: AsyncSession,
        db_worker: DbWriterWorker,
    ) -> ParsePostsFromDirectory:
        return ParsePostsFromDirectory(
            config=parse_config,
            tag_data_mapper=tag_data_mapper,
            directory_discoverer=directory_discoverer,
            transaction=transaction,
            db_worker=db_worker,
        )

    @provide(scope=Scope.SESSION)
    async def get_create_user(
        self, session: AsyncSession, user_data_mapper: UserDataMapper, password_hasher: PasswordHasher
    ) -> CreateUser:
        return CreateUser(user_data_mapper=user_data_mapper, password_hasher=password_hasher, transaction=session)

    @provide(scope=Scope.REQUEST)
    def get_activate_post(self, posts_data_mapper: PostDataMapper, session: AsyncSession) -> ActivatePost:
        return ActivatePost(posts_data_mapper=posts_data_mapper, transaction=session)

    @provide(scope=Scope.REQUEST)
    def get_deactivate_post(self, posts_data_mapper: PostDataMapper, session: AsyncSession) -> DeactivatePost:
        return DeactivatePost(posts_data_mapper=posts_data_mapper, transaction=session)

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
