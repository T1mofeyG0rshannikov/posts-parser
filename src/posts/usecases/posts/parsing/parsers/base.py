import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from posts.dto.parse_posts import ParseUsecaseResponse
from posts.interfaces.logger import Logger
from posts.interfaces.transaction import Transaction
from posts.persistence.data_mappers.tag_data_mapper import TagDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.db_writer_worker import DbWriterWorker
from posts.usecases.posts.parsing.file_discoverers.base import FileDiscoverer
from posts.usecases.posts.parsing.parser_worker import ParserWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class ParsePosts:
    """
    Асинхронный менеджер процесса парсинга HTML-постов и записи результатов в базу данных.

    Класс управляет всем жизненным циклом парсинга:
    1. Сканирует HTML-файлы через FileDiscoverer.
    2. Передаёт пути к файлам в очередь file_q.
    3. Несколько ParserWorker читают файлы и парсят их в структуры ParsedPostDTO.
    4. Готовые объекты помещаются в очередь parsed_q.
    5. DbWriterWorker считывает данные из parsed_q и пакетно сохраняет их в базу данных через PostDataMapper.

    Attributes:
        _config (ParseConfig): Конфигурация процесса парсинга (размер батча, таймауты, пути и т.п.).
        _file_q (asyncio.Queue[str]): Очередь с путями к HTML-файлам, которые нужно обработать.
        _parsed_q (asyncio.Queue[ParsedPostDTO]): Очередь с готовыми результатами парсинга.
        _db_writer_worker (DbWriterWorker): Асинхронный воркер для записи результатов в базу.
        _executor (ThreadPoolExecutor): Пул потоков для выполнения парсинга HTML.
        _parser_workers (list[ParserWorker]): Список воркеров, выполняющих парсинг HTML-файлов.
        _file_discoverer (FileDiscoverer): Объект, отвечающий за поиск HTML-файлов.
        _transaction (Transaction): Объект управляющий транзакцией бд

    """

    def __init__(
        self,
        config: ParseConfig,
        tag_data_mapper: TagDataMapper,
        file_discoverer: FileDiscoverer,
        db_worker: DbWriterWorker,
        transaction: Transaction,
        logger: Logger,
    ) -> None:
        self._config = config
        self._file_q: asyncio.Queue = asyncio.Queue(maxsize=config.FILE_QUEUE_MAX)
        self._parsed_q: asyncio.Queue = asyncio.Queue(maxsize=config.PARSED_QUEUE_MAX)
        db_worker.set_parsed_q(self._parsed_q)
        self._db_writer_worker = db_worker
        self._logger = logger
        self._executor = ThreadPoolExecutor(max_workers=self._config.N_PARSER_WORKERS)
        lock = asyncio.Lock()
        self._lock = lock
        parsed_ids: set[int] = set()
        self._parser_workers = [
            ParserWorker(
                i, self._executor, self._file_q, self._parsed_q, lock=lock, parsed_ids=parsed_ids, logger=logger
            )
            for i in range(self._config.N_PARSER_WORKERS)
        ]
        self._file_discoverer = file_discoverer
        self._file_discoverer.bind_file_q(self._file_q)
        self._tag_data_mapper = tag_data_mapper
        self._transaction = transaction
        self._skipped = 0
        self._invalid = 0
        self._inserted = 0

    async def _increment_counter(
        self, counter: Literal["inserted", "skipped", "invalid"], in_lock: bool, value: int
    ) -> None:
        attr_name = f"_{counter}"
        if in_lock:
            async with self._lock:
                setattr(self, attr_name, getattr(self, attr_name) + value)
        else:
            setattr(self, attr_name, getattr(self, attr_name) + value)

    async def increment_skipped(self, value: int = 1, in_lock=False):
        await self._increment_counter(counter="skipped", value=value, in_lock=in_lock)

    async def increment_inserted(self, value: int = 1, in_lock=False):
        await self._increment_counter(counter="inserted", value=value, in_lock=in_lock)

    async def increment_invalid(self, value: int = 1, in_lock=False):
        await self._increment_counter(counter="invalid", value=value, in_lock=in_lock)

    async def __call__(self) -> ParseUsecaseResponse:
        start = time.time()

        exist_tags = await self._tag_data_mapper.all()

        tags_dict = {tag.slug: tag.id for tag in exist_tags}

        discover_task = asyncio.create_task(self._file_discoverer.discover())
        parser_tasks = [
            asyncio.create_task(
                parser_worker(skipped_callback=self.increment_skipped, invalid_callback=self.increment_invalid)
            )
            for parser_worker in self._parser_workers
        ]
        db_writer = asyncio.create_task(
            self._db_writer_worker(
                tags_dict=tags_dict, skipped_callback=self.increment_skipped, inserted_callback=self.increment_inserted
            )
        )
        await discover_task
        await self._file_q.join()
        await asyncio.gather(*parser_tasks)
        await self._parsed_q.join()
        await db_writer
        await self._transaction.commit()

        self._executor.shutdown(wait=True)

        print(time.time() - start)
        logging.info("All done")

        return ParseUsecaseResponse(skipped=self._skipped, inserted=self._inserted, invalid=self._invalid)
