from posts.persistence.models import PostOrm
from posts.posts.models import PostWithTags, Tag


def from_orm_to_post_with_tags(post: PostOrm) -> PostWithTags:
    return PostWithTags(
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
        tags=[
            Tag(
                id=post_tag.tag.id,
                name=post_tag.tag.name,
                slug=post_tag.tag.slug,
            )
            for post_tag in post.tags
        ],
    )
