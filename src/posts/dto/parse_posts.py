from dataclasses import dataclass
from datetime import time


@dataclass
class ParsedPostTagDTO:
    slug: str
    name: str

    def __hash__(self):
        return hash(self.slug)


@dataclass
class ParsedPostDTO:
    title: str
    id: str
    description: str
    published: time
    h1: str
    image: str
    content: str
    content2: str
    slug: str
    tags: list[ParsedPostTagDTO]
    active: bool
