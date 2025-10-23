from dataclasses import dataclass


@dataclass
class WordpressPostDTO:
    title: str
    content: str
    description: str
    featured_media: int
    image_name: str
    tags: list[int]  # list of Wp tag ids

    published: str

    h1: str

    slug: str
    status: str = "publish"
