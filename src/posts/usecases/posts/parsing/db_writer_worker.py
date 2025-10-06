import asyncio
import logging

from posts.persistence.posts_data_mapper import PostDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.parsing.dto import ParsedPostDTO


class DbWriterWorker:
    """
    Асинхронный воркер, выполняющий пакетную запись результатов парсинга в базу данных.

    Класс получает объекты ParsedPostDTO из очереди parsed_q, накапливает их в батчи
    и сохраняет через PostDataMapper.

    Args:
        parsed_q (asyncio.Queue): Очередь с готовыми результатами парсинга.
        config (ParseConfig): Конфигурация, задающая размер батча, и количество парсеров.
        posts_data_mapper (PostDataMapper): Класс для сохранения постов в базу данных.
    """

    def __init__(self, parsed_q: asyncio.Queue, config: ParseConfig, posts_data_mapper: PostDataMapper) -> None:
        self._parsed_q = parsed_q
        self._config = config
        self._data_mapper = posts_data_mapper

    async def __call__(self) -> None:
        exist_posts = await self._data_mapper.all_ids()
        batch: list[ParsedPostDTO] = []
        shutdown_signals = 0

        while True:
            item = await asyncio.wait_for(self._parsed_q.get(), timeout=None)

            if item is None:
                shutdown_signals += 1
                self._parsed_q.task_done()

                if shutdown_signals >= self._config.N_PARSER_WORKERS:
                    if batch:
                        await self._data_mapper.bulk_save(batch)
                        batch.clear()
                    logging.info("DB writer shutdown after %d signals", shutdown_signals)
                    break
                continue

            if item.id not in exist_posts:
                batch.append(item)
            self._parsed_q.task_done()

            if len(batch) >= self._config.BATCH_SIZE:
                await self._data_mapper.bulk_save(batch)
                batch.clear()
