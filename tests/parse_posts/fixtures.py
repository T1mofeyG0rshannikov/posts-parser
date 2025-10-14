import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from posts.persistence.data_mappers.error_log_data_mapper import ErrorLogDataMapper
from posts.persistence.data_mappers.posts_data_mapper import PostDataMapper
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.services import DbLogger
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.db_writer_worker import DbWriterWorker
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.directory_discoverer import (
    DirectoryDiscoverer,
)
from posts.usecases.posts.parsing.file_discoverers.zip_archive_discoverer import (
    ZIPDiscoverer,
)
from posts.usecases.posts.parsing.parsers.directory_parser import (
    ParsePostsFromDirectory,
)
from posts.usecases.posts.parsing.parsers.zip_parser import ParsePostsFromZIP
from posts.usecases.posts.persist_posts import PersistPosts


@pytest.fixture
def parse_config() -> ParseConfig:
    return ParseConfig()


@pytest.fixture
def post_data_mapper(db: AsyncSession) -> PostDataMapper:
    return PostDataMapper(db)


@pytest.fixture
def tag_data_mapper(db: AsyncSession) -> TagDataMapper:
    return TagDataMapper(db)


@pytest.fixture
def persist_posts(post_data_mapper: PostDataMapper, tag_data_mapper: TagDataMapper) -> PersistPosts:
    return PersistPosts(post_data_mapper=post_data_mapper, tag_data_mapper=tag_data_mapper)


@pytest.fixture
def db_worker(
    parse_config: ParseConfig, persist_posts: PersistPosts, post_data_mapper: PostDataMapper
) -> DbWriterWorker:
    return DbWriterWorker(config=parse_config, persist_posts=persist_posts, post_data_mapper=post_data_mapper)


@pytest.fixture
def zip_discoverer(parse_config: ParseConfig) -> ZIPDiscoverer:
    return ZIPDiscoverer(n_parser_workers=parse_config.N_PARSER_WORKERS)


@pytest.fixture
def directory_discoverer(parse_config: ParseConfig) -> DirectoryDiscoverer:
    return DirectoryDiscoverer(config=parse_config, n_parser_workers=parse_config.N_PARSER_WORKERS)


@pytest.fixture
def error_log_data_mapper(db: AsyncSession) -> ErrorLogDataMapper:
    return ErrorLogDataMapper(db)


@pytest.fixture
def logger(error_log_data_mapper: ErrorLogDataMapper, db: AsyncSession) -> DbLogger:
    return DbLogger(error_log_data_mapper=error_log_data_mapper, transaction=db)


@pytest.fixture
def parse_posts_from_zip(
    parse_config: ParseConfig,
    db_worker: DbWriterWorker,
    zip_discoverer: ZIPDiscoverer,
    db: AsyncSession,
    tag_data_mapper: TagDataMapper,
    logger: DbLogger,
) -> ParsePostsFromZIP:
    return ParsePostsFromZIP(
        config=parse_config,
        db_worker=db_worker,
        zip_discoverer=zip_discoverer,
        transaction=db,
        tag_data_mapper=tag_data_mapper,
        logger=logger,
    )


@pytest.fixture
def parse_posts_from_directory(
    parse_config: ParseConfig,
    db_worker: DbWriterWorker,
    directory_discoverer: DirectoryDiscoverer,
    db: AsyncSession,
    tag_data_mapper: TagDataMapper,
    logger: DbLogger,
) -> ParsePostsFromDirectory:
    return ParsePostsFromDirectory(
        config=parse_config,
        db_worker=db_worker,
        directory_discoverer=directory_discoverer,
        transaction=db,
        tag_data_mapper=tag_data_mapper,
        logger=logger,
    )
