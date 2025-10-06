from pydantic_settings import BaseSettings


class DirectoryDiscovererConfig(BaseSettings):
    DATA_DIR: str

    class Config:
        env_file = ".env"
        extra = "allow"
