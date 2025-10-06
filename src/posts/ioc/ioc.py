from dishka import Provider, Scope, from_context, provide
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from posts.admin.admin import CustomAdmin
from posts.admin.auth.backend import AdminAuth
from posts.admin.auth.login_factory.dishka_login_factory import DishkaLoginFactory
from posts.admin.config import AdminConfig
from posts.persistence.posts_data_mapper import PostDataMapper
from posts.persistence.user_data_mapper import UserDataMapper
from posts.usecases.create_user import CreateUser
from posts.usecases.posts.avtivate import ActivatePost
from posts.usecases.posts.deavtivate import DeactivatePost
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.config import (
    DirectoryDiscovererConfig,
)
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.directory_discoverer import (
    DirectoryDiscoverer,
)
from posts.usecases.posts.parsing.parsers.base import ParsePosts
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

    posts_data_mapper = provide(PostDataMapper, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_directory_discoverer(
        self, directory_discoverer_config: DirectoryDiscovererConfig, parse_config: ParseConfig
    ) -> DirectoryDiscoverer:
        return DirectoryDiscoverer(config=directory_discoverer_config, n_parser_workers=parse_config.N_PARSER_WORKERS)

    @provide(scope=Scope.APP)
    def get_parse_posts_from_directory_interactor(
        self,
        parse_config: ParseConfig,
        posts_data_mapper: PostDataMapper,
        directory_discoverer: DirectoryDiscoverer,
        transaction: AsyncSession,
    ) -> ParsePosts:
        return ParsePosts(
            config=parse_config,
            data_mapper=posts_data_mapper,
            file_discoverer=directory_discoverer,
            transaction=transaction,
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
