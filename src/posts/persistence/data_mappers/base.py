from sqlalchemy.ext.asyncio import AsyncSession


class BaseDataMapper:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
