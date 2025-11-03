import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from posts.interfaces.logger import Logger
from posts.usecases.posts.parsing.html_parser import parse_html


class ParserWorker:
    """
    Асинхронный воркер, выполняющий чтение и парсинг HTML-файлов.

    ParserWorker отвечает за обработку задач из очереди file_q:
    он асинхронно читает HTML-файлы, выполняет их парсинг в пуле потоков (ThreadPoolExecutor),
    и помещает результат в очередь parsed_q для дальнейшей обработки.

    Для предотвращения дубликатов используется общий parsed_ids set, доступ к которому синхронизирован
    с помощью asyncio lock.

    Args:
        name (str): Уникальное имя воркера.
        executor (ThreadPoolExecutor): Пул потоков для выполнения CPU-блокирующих задач.
        file_q (asyncio.Queue): Очередь с контентом файла в качестве строки для парсинга.
        parsed_q (asyncio.Queue): Очередь для результатов парсинга.
        lock (asyncio.Lock): Замок для синхронизации работы с _parsed_ids.
        parsed_ids (set[int]): Множество ID уже спарсенных постов.
        skipped (int): Кол-во пропущенных постов(дубликаты)
    Methods:
        call(): Основной цикл воркера, извлекает задачи из очереди, парсит HTML и сохраняет результат.
    """

    def __init__(
        self,
        name: str,
        executor: ThreadPoolExecutor,
        file_q: asyncio.Queue,
        parsed_q: asyncio.Queue,
        lock: asyncio.Lock,
        parsed_ids: set[int],
        logger: Logger,
    ) -> None:
        self._name = name
        self._executor = executor
        self._file_q = file_q
        self._parsed_q = parsed_q
        self._lock = lock
        self._parsed_ids = parsed_ids
        self._logger = logger

    async def __call__(self, skipped_callback, invalid_callback) -> None:
        loop = asyncio.get_running_loop()

        while True:
            html = await self._file_q.get()
            if html is None:
                await self._parsed_q.put(None)
                self._file_q.task_done()
                logging.info("Parser %s got shutdown", self._name)
                break

            parsed_response = await loop.run_in_executor(self._executor, parse_html, html)

            if not parsed_response.success:
                await self._parsed_q.put(0)
                await invalid_callback(in_lock=True)
                await self._logger.log(
                    title=f"Не удалось добавить пост с id {parsed_response.data}", message=parsed_response.error_message
                )
                self._file_q.task_done()
                continue

            parsed = parsed_response.data

            async with self._lock:
                if parsed.id not in self._parsed_ids:
                    await self._parsed_q.put(parsed)
                    self._parsed_ids.add(parsed.id)
                else:
                    await skipped_callback()

            self._file_q.task_done()
