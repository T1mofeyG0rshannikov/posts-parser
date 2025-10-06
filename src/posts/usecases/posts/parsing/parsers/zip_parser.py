from zipfile import ZipFile

from posts.interfaces.transaction import Transaction
from posts.persistence.posts_data_mapper import PostDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.file_discoverers.zip_archive_discoverer import (
    ZIPDiscoverer,
)
from posts.usecases.posts.parsing.parsers.base import ParsePosts


class ParsePostsFromZIP(ParsePosts):
    """
    Асинхронный менеджер процесса парсинга HTML-постов из zip архива в виде объекта ZipFile и записи результатов в базу данных.
    """

    def __init__(
        self, config: ParseConfig, data_mapper: PostDataMapper, zip_discoverer: ZIPDiscoverer, transaction: Transaction
    ) -> None:
        super().__init__(
            config=config, data_mapper=data_mapper, file_discoverer=zip_discoverer, transaction=transaction
        )

    async def __call__(self, zip_file: ZipFile) -> None:
        self._file_discoverer.set_file(zip_file)
        return await super().__call__()
