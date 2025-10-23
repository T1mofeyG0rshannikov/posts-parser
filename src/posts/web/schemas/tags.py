from pydantic import BaseModel

from posts.dto.post import Tag


class AllTagsResponse(BaseModel):
    tags: list[Tag]
