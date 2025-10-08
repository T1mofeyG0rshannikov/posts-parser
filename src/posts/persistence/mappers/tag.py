from posts.dto.post_tag_relation import PostTagRelation
from posts.persistence.mappers.post import from_orm_to_post
from posts.persistence.models import PostTagOrm, TagOrm
from posts.posts.models import Tag, TagWithPosts


def from_orm_to_tag(tag: TagOrm) -> Tag:
    return Tag(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
    )


def from_orm_to_post_tag(relation: PostTagOrm) -> PostTagRelation:
    return PostTagRelation(post_id=relation.post_id, tag_id=relation.tag_id)


def from_orm_to_tag_with_posts(tag: TagOrm) -> TagWithPosts:
    return TagWithPosts(
        id=tag.id, name=tag.name, slug=tag.slug, posts=[from_orm_to_post(relation.post) for relation in tag.posts]
    )
