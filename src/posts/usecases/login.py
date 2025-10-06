from posts.exceptions import AccessDeniedError, InvalidPasswordError, UserNotFoundError
from posts.persistence.user_data_mapper import UserDataMapper
from posts.user.access_token import AccessToken
from posts.user.auth.jwt_processor import JwtProcessor
from posts.user.password_hasher import PasswordHasher


class Login:
    def __init__(
        self,
        user_data_mapper: UserDataMapper,
        jwt_processor: JwtProcessor,
        password_hasher: PasswordHasher,
    ) -> None:
        self.data_mapper = user_data_mapper
        self.jwt_processor = jwt_processor
        self.password_hasher = password_hasher

    async def __call__(self, username: str, password: str, superuser_required: bool = False) -> AccessToken:
        user = await self.data_mapper.get_by_username(username)
        if not user:
            raise UserNotFoundError(f'нет пользователя с username "{username}"')

        if superuser_required and not user.is_superuser:
            raise AccessDeniedError("Пользователь не является админом")

        if not self.password_hasher.verify(password, user.hash_password):
            raise InvalidPasswordError("Неверный пароль")

        access_token = self.jwt_processor.create_access_token(user.username, user.id)
        return access_token
