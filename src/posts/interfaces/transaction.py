from asyncio import Protocol


class Transaction(Protocol):
    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
