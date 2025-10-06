from posts.persistence.posts_data_mapper import PostDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.directory_discoverer import (
    DirectoryDiscoverer,
)
from posts.usecases.posts.parsing.parsers.base import ParsePosts


class ParsePostsFromDirectory(ParsePosts):
    """
    Асинхронный менеджер процесса парсинга HTML-постов из директории на сервере и записи результатов в базу данных.
    """

    def __init__(
        self, config: ParseConfig, data_mapper: PostDataMapper, directory_discoverer: DirectoryDiscoverer
    ) -> None:
        super().__init__(config=config, data_mapper=data_mapper, file_discoverer=directory_discoverer)
