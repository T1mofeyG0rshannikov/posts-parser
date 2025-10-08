from pydantic import BaseModel

from posts.posts.models import Tag


class AllTagsResponse(BaseModel):
    tags: list[Tag]
