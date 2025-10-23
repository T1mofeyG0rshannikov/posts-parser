from posts.dto.post import Post
from posts.persistence.models import PostOrm


def from_orm_to_post(post: PostOrm) -> Post:
    return Post(
        id=post.id,
        title=post.title,
        description=post.description,
        published=post.published,
        h1=post.h1,
        image=post.image,
        content=post.content,
        content2=post.content2,
        slug=post.slug,
        active=post.active,
    )
