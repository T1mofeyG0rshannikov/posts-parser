from dishka import Provider, Scope, provide

from posts.persistence.data_mappers.user_data_mapper import UserDataMapper
from posts.usecases.login import Login
from posts.user.auth.jwt_config import JwtConfig
from posts.user.auth.jwt_processor import JwtProcessor
from posts.user.password_hasher import PasswordHasher


class LoginProvider(Provider):
    @provide(scope=Scope.APP)
    def get_jwt_config(self) -> JwtConfig:
        return JwtConfig()

    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def get_jwt_processor(self, jwt_config: JwtConfig) -> JwtProcessor:
        return JwtProcessor(jwt_config)

    @provide(scope=Scope.REQUEST)
    async def get_login(
        self, user_data_mapper: UserDataMapper, jwt_processor: JwtProcessor, password_hasher: PasswordHasher
    ) -> Login:
        return Login(
            user_data_mapper=user_data_mapper,
            jwt_processor=jwt_processor,
            password_hasher=password_hasher,
        )
