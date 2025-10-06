from pydantic_settings import BaseSettings


class AdminConfig(BaseSettings):
    secret_key: str
    debug: bool
    templates_dir: str

    class Config:
        extra = "allow"
        env_file = ".env"
