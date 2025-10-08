import os

import aiofiles  # type: ignore

from posts.usecases.posts.parsing.file_discoverers.base import FileDiscoverer
from posts.usecases.posts.parsing.file_discoverers.directory_discoverer.config import (
    DirectoryDiscovererConfig,
)


class DirectoryDiscoverer(FileDiscoverer):
    def __init__(self, config: DirectoryDiscovererConfig, n_parser_workers: int) -> None:
        super().__init__()
        self._config = config
        self._N_PARSER_WORKERS = n_parser_workers

    async def discover(self) -> None:
        for dirpath, _, filenames in os.walk(self._config.DATA_DIR):
            for fn in filenames:
                if not fn.lower().endswith((".html", ".htm", "-")):
                    continue
                path = os.path.join(dirpath, fn)

                async with aiofiles.open(path, "r", encoding="utf-8", errors="ignore") as f:
                    html = await f.read()

                await self.file_q.put(html)

        for _ in range(self._N_PARSER_WORKERS):
            await self.file_q.put(None)
