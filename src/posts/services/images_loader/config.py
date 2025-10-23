from pydantic import Field
from pydantic_settings import BaseSettings


class PostsImagsLoaderConfig(BaseSettings):
    images_dir: str = Field(alias="POST_IMAGES_DIR")

    class Config:
        extra = "allow"
        env_file = ".env"
