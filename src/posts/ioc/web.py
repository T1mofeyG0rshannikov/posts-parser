from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.services import DbLogger
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.db_writer_worker import DbWriterWorker
from posts.usecases.posts.parsing.file_discoverers.zip_archive_discoverer import (
    ZIPDiscoverer,
)
from posts.usecases.posts.parsing.parsers.zip_parser import ParsePostsFromZIP


class WebProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_zip_archive_discoverer(self, parse_config: ParseConfig) -> ZIPDiscoverer:
        return ZIPDiscoverer(n_parser_workers=parse_config.N_PARSER_WORKERS)

    @provide(scope=Scope.REQUEST)
    def get_web_parse_posts(
        self,
        session: AsyncSession,
        parse_config: ParseConfig,
        db_worker: DbWriterWorker,
        tag_data_mapper: TagDataMapper,
        zip_archive_discoverer: ZIPDiscoverer,
        logger: DbLogger,
    ) -> ParsePostsFromZIP:
        return ParsePostsFromZIP(
            config=parse_config,
            db_worker=db_worker,
            tag_data_mapper=tag_data_mapper,
            zip_discoverer=zip_archive_discoverer,
            transaction=session,
            logger=logger,
        )
