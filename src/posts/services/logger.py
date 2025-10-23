from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from posts.interfaces.logger import Logger
from posts.persistence.data_mappers.error_log_data_mapper import ErrorLogDataMapper


class DbLogger(Logger):
    """
    Класс, предназначенный для логирования ошибок и сохранения их в базе данных.

    Для обеспечения большей автономности, класс самостоятельно управляет сессией базы данных,
    выполняя коммит транзакций после записи лога.  Это позволяет использовать логгер
    без необходимости явного управления транзакциями извне.

    Args:
        error_log_data_mapper (ErrorLogDataMapper):  Объект DataMapper, отвечающий за взаимодействие
                                  с таблицей логов ошибок в базе данных.
        transaction (Transaction): Объект Transaction, представляет текущую транзакцию базы данных.
    """

    def __init__(
        self, error_log_data_mapper: ErrorLogDataMapper, session_maker: async_sessionmaker[AsyncSession]
    ) -> None:
        self._error_log_data_mapper = error_log_data_mapper
        self._session_maker = session_maker

    async def log(self, title: str, message: str) -> None:
        async with self._session_maker() as session:
            await self._error_log_data_mapper.create(title=title, message=message)
            await session.commit()
