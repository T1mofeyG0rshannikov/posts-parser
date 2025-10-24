from dataclasses import dataclass

from posts.dto.post import Post


@dataclass
class WordpressPostDTO:
    title: str
    content: str
    description: str
    featured_media: int
    image_name: str
    tags: list[int]  # list of Wp tag ids

    publish: str

    h1: str

    slug: str
    status: str = "publish"

    @staticmethod
    def generate_slug(post: Post):
        slug = post.slug
        while slug[0] == "-" or slug[0] == "_":
            slug = slug[1::]

        return f"{post.id}-{slug}"
