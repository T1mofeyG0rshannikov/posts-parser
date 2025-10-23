from dataclasses import dataclass
from datetime import date


@dataclass
class Tag:
    id: int
    name: str
    slug: str

    def __str__(self) -> str:
        return self.name

    def __eq__(self, tag):
        return self.slug == tag.slug


@dataclass
class Post:
    id: int

    title: str
    description: str
    published: date

    h1: str
    image: str
    content: str
    content2: str

    slug: str

    active: bool


@dataclass
class PostWithTags(Post):
    tags: list[Tag]

    def __hash__(self):
        return hash(self.id)


@dataclass
class TagWithPosts(Tag):
    posts: list[Post]
