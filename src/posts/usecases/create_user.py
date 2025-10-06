from sqlalchemy.ext.asyncio import AsyncSession

from posts.exceptions import InvalidPasswordError, UserWithUsernameAlreadyExistError
from posts.persistence.user_data_mapper import UserDataMapper
from posts.user.model import User
from posts.user.password_hasher import PasswordHasher
from posts.user.validate_password import validate_password


class CreateUser:
    def __init__(
        self,
        user_data_mapper: UserDataMapper,
        password_hasher: PasswordHasher,
        transaction: AsyncSession,
    ) -> None:
        self.data_mapper = user_data_mapper
        self.transaction = transaction
        self.password_hasher = password_hasher

    async def __call__(self, password: str, username: str, is_superuser: bool = False) -> User:
        if not validate_password(password):
            raise InvalidPasswordError("Пароль должен быть от 6 символов")

        hashed_password = self.password_hasher.hash_password(password)

        user_by_username = await self.data_mapper.get_by_username(username)
        if user_by_username is not None:
            raise UserWithUsernameAlreadyExistError(f"User with username '{username}' already exist")

        user = User(
            username=username,
            hash_password=hashed_password,
            is_superuser=is_superuser,
        )

        await self.data_mapper.save(user)
        await self.transaction.commit()
        return user
