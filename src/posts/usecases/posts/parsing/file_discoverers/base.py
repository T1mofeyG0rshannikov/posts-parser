import asyncio
from abc import ABC, abstractmethod


class FileDiscoverer(ABC):
    def __init__(self) -> None:
        self._file_q: asyncio.Queue | None = None

    def bind_file_q(self, file_q: asyncio.Queue) -> None:
        self._file_q = file_q

    @property
    def file_q(self) -> asyncio.Queue:
        if self._file_q is None:
            raise ValueError("no file_q set")
        return self._file_q

    @abstractmethod
    async def discover(self) -> None:
        ...
