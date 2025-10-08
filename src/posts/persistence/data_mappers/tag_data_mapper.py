from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from posts.dto.parse_posts import ParsedPostTagDTO
from posts.dto.post_tag_relation import PostTagRelation
from posts.persistence.data_mappers.base import BaseDataMapper
from posts.persistence.mappers.tag import (
    from_orm_to_post_tag,
    from_orm_to_tag,
    from_orm_to_tag_with_posts,
)
from posts.persistence.models import PostTagOrm, TagOrm
from posts.posts.models import Tag, TagWithPosts


class TagDataMapper(BaseDataMapper):
    async def get(self, id: int) -> Tag:
        result = await self._session.get(TagOrm, id)
        return from_orm_to_tag(result) if result else None

    async def get_with_posts(self, id: int) -> TagWithPosts:
        result = await self._session.execute(
            select(TagOrm).options(selectinload(TagOrm.posts).selectinload(PostTagOrm.post)).where(TagOrm.id == id)
        )

        tag = result.scalar()
        return from_orm_to_tag_with_posts(tag) if tag else None

    async def all(self) -> list[Tag]:
        results = await self._session.execute(select(TagOrm))
        results = results.scalars().all()
        return [from_orm_to_tag(tag) for tag in results]

    async def bulk_save(self, tags: list[ParsedPostTagDTO]) -> list[Tag]:
        tags_orm = [TagOrm(name=tag.name, slug=tag.slug) for tag in tags]

        self._session.add_all(tags_orm)

        await self._session.flush()
        return [from_orm_to_tag(tag) for tag in tags_orm]

    async def get_relation(self, tag_id: int, post_id: int) -> PostTagRelation | None:
        result = await self._session.execute(
            select(PostTagOrm).where(PostTagOrm.tag_id == tag_id, PostTagOrm.post_id == post_id)
        )
        result = result.scalar()
        return from_orm_to_post_tag(result) if result else None

    async def save_post_relation(self, tag_id: int, post_id: int) -> None:
        relation = PostTagOrm(tag_id=tag_id, post_id=post_id)

        self._session.add(relation)

    async def bulk_save_post_relations(self, relations: list[PostTagRelation]) -> None:
        relations_orm = [PostTagOrm(post_id=relation.post_id, tag_id=relation.tag_id) for relation in relations]

        self._session.add_all(relations_orm)

    async def delete_post_tag_relation(self, post_id: int, tag_id: int) -> None:
        await self._session.execute(
            delete(PostTagOrm).where(PostTagOrm.tag_id == tag_id, PostTagOrm.post_id == post_id)
        )
