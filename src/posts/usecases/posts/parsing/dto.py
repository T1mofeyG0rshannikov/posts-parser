from dataclasses import dataclass
from datetime import time


@dataclass
class ParsedPostTagDTO:
    slug: str
    name: str


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
