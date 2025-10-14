from posts.persistence.data_mappers.base import BaseDataMapper
from posts.persistence.models import ErrorLogOrm


class ErrorLogDataMapper(BaseDataMapper):
    async def create(self, title: str, message: str) -> None:
        error_log = ErrorLogOrm(title=title, message=message)

        self._session.add(error_log)
