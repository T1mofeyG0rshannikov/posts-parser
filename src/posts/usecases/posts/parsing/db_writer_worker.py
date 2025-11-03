import asyncio
import logging

from posts.dto.parse_posts import ParsedPostDTO
from posts.persistence.data_mappers.post_data_mapper import PostDataMapper
from posts.usecases.posts.parsing.config import ParseConfig
from posts.usecases.posts.persist_posts import PersistPosts


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

    def __init__(self, config: ParseConfig, persist_posts: PersistPosts, post_data_mapper: PostDataMapper) -> None:
        self._parsed_q: asyncio.Queue | None = None
        self._config = config
        self._persist_posts = persist_posts
        self._data_mapper = post_data_mapper

    def set_parsed_q(self, parsed_q: asyncio.Queue):
        self._parsed_q = parsed_q

    async def __call__(self, tags_dict: dict[str, int], skipped_callback, inserted_callback) -> None:
        if self._parsed_q is None:
            raise ValueError("no parsed_q set")

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
                        try:
                            await self._persist_posts(batch, tags_dict=tags_dict)
                            print("send_in_db", len(batch))
                            await inserted_callback(value=len(batch), in_lock=True)
                            batch.clear()
                        except Exception as e:
                            print(e)
                    logging.info("DB writer shutdown after %d signals", shutdown_signals)
                    break
                continue

            if item == 0:
                self._parsed_q.task_done()
            else:
                if item.id not in exist_posts:
                    batch.append(item)
                else:
                    await skipped_callback(in_lock=True)

                self._parsed_q.task_done()

                if len(batch) >= self._config.BATCH_SIZE:
                    await self._persist_posts(batch, tags_dict=tags_dict)
                    print("send_in_db", len(batch))
                    batch.clear()
