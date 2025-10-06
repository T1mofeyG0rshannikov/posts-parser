import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from posts.interfaces.transaction import Transaction
from posts.persistence.posts_data_mapper import PostDataMapper
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
        data_mapper: PostDataMapper,
        file_discoverer: FileDiscoverer,
        transaction: Transaction,
    ) -> None:
        self._config = config
        self._file_q: asyncio.Queue = asyncio.Queue(maxsize=config.FILE_QUEUE_MAX)
        self._parsed_q: asyncio.Queue = asyncio.Queue(maxsize=config.PARSED_QUEUE_MAX)
        self._db_writer_worker = DbWriterWorker(parsed_q=self._parsed_q, posts_data_mapper=data_mapper, config=config)
        self._executor = ThreadPoolExecutor(max_workers=self._config.N_PARSER_WORKERS)
        lock = asyncio.Lock()
        parsed_ids: set[int] = set()
        self._parser_workers = [
            ParserWorker(i, self._executor, self._file_q, self._parsed_q, lock=lock, parsed_ids=parsed_ids)
            for i in range(self._config.N_PARSER_WORKERS)
        ]
        self._file_discoverer = file_discoverer
        self._file_discoverer.bind_file_q(self._file_q)
        self._transaction = transaction

    async def __call__(self) -> None:
        import time

        start = time.time()
        discover_task = asyncio.create_task(self._file_discoverer.discover())
        parser_tasks = [asyncio.create_task(parser_worker()) for parser_worker in self._parser_workers]
        db_writer = asyncio.create_task(self._db_writer_worker())
        await discover_task
        discover_task.done()
        await self._file_q.join()
        await asyncio.gather(*parser_tasks)
        await self._parsed_q.join()
        await db_writer
        db_writer.done()
        await self._transaction.commit()
        print(time.time() - start)
        self._executor.shutdown(wait=True)
        logging.info("All done")
