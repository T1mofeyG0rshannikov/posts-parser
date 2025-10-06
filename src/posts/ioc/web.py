from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from posts.persistence.posts_data_mapper import PostDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.file_discoverers.zip_archive_discoverer import (
    ZIPDiscoverer,
)
from posts.usecases.posts.parsing.parsers.base import ParsePosts
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
        posts_data_mapper: PostDataMapper,
        zip_archive_discoverer: ZIPDiscoverer,
    ) -> ParsePostsFromZIP:
        return ParsePostsFromZIP(
            config=parse_config,
            data_mapper=posts_data_mapper,
            zip_discoverer=zip_archive_discoverer,
            transaction=session,
        )
