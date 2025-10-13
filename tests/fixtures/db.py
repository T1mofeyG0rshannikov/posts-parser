import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from posts.persistence.models import Model


@pytest.fixture
def engine():
    return create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)


async def create_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


@pytest.fixture
async def db(engine):
    await delete_tables(engine)
    await create_tables(engine)
    new_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with new_session() as session:
        yield session


@pytest.fixture
async def transaction(engine):
    new_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with new_session() as session:
        yield session
