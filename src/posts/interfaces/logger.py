from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    async def log(self, title: str, message: str) -> None:
        ...
