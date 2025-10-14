from posts.interfaces.logger import Logger
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.db_writer_worker import DbWriterWorker
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.directory_discoverer import (
    DirectoryDiscoverer,
)
from posts.usecases.posts.parsing.parsers.base import ParsePosts


class ParsePostsFromDirectory(ParsePosts):
    """
    Асинхронный менеджер процесса парсинга HTML-постов из директории на сервере и записи результатов в базу данных.
    """

    def __init__(
        self,
        config: ParseConfig,
        directory_discoverer: DirectoryDiscoverer,
        db_worker: DbWriterWorker,
        tag_data_mapper: TagDataMapper,
        transaction: Transaction,
        logger: Logger,
    ) -> None:
        super().__init__(
            config=config,
            tag_data_mapper=tag_data_mapper,
            file_discoverer=directory_discoverer,
            db_worker=db_worker,
            transaction=transaction,
            logger=logger,
        )
