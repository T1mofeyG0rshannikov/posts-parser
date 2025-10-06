from abc import ABC, abstractmethod

from posts.usecases.login import Login


class LoginFactory(ABC):
    @abstractmethod
    async def __call__(self) -> Login:
        ...
