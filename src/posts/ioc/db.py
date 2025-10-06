from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from posts.persistence.db.db_config import DbConfig
from posts.persistence.user_data_mapper import UserDataMapper


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def get_db_config(self) -> DbConfig:
        return DbConfig()

    @provide(scope=Scope.APP)
    def get_engine(self, db_config: DbConfig) -> AsyncEngine:
        return create_async_engine(db_config.DATABASE_URL, pool_size=15, max_overflow=50, pool_timeout=30)

    @provide(scope=Scope.APP)
    async def get_session_maker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.APP)
    async def get_session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.SESSION)
    async def get_user_data_mapper(self, session: AsyncSession) -> UserDataMapper:
        return UserDataMapper(session=session)
