from sqlalchemy import select

from posts.persistence.data_mappers.base import BaseDataMapper
from posts.persistence.mappers.user import from_orm_to_user
from posts.persistence.models import UserOrm
from posts.user.model import User


class UserDataMapper(BaseDataMapper):
    async def get(self, id: int) -> User | None:
        result = await self._session.execute(select(UserOrm).where(UserOrm.id == id))

        user = result.scalar()
        return from_orm_to_user(user) if user else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(UserOrm).where(UserOrm.username == username))

        user = result.scalar()
        return from_orm_to_user(user) if user else None

    async def save(self, user: User) -> None:
        user = UserOrm(
            username=user.username,
            hash_password=user.hash_password,
            is_superuser=user.is_superuser,
        )
        self._session.add(user)
