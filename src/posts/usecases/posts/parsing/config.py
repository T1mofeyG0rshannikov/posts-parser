import os

from pydantic_settings import BaseSettings


class ParseConfig(BaseSettings):
    DATA_DIR: str = "C:/Users/tgors/Desktop/articles/articles"
    N_PARSER_WORKERS: int = min(32, (os.cpu_count() or 4) * 2)
    DB_POOL_MIN: int = 5
    DB_POOL_MAX: int = 20
    PARSED_QUEUE_MAX: int = 20000
    FILE_QUEUE_MAX: int = 20000
    BATCH_SIZE: int = 1000
    BATCH_MAX_WAIT: float = 10000.0
