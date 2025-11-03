from dataclasses import asdict

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload

from posts.dto.parse_posts import ParsedPostDTO
from posts.dto.post import Post, PostWithTags
from posts.persistence.data_mappers.base import BaseDataMapper
from posts.persistence.mappers.post_with_tags import from_orm_to_post_with_tags
from posts.persistence.models import PostOrm, PostTagOrm


class PostDataMapper(BaseDataMapper):
    async def save(self, post: Post) -> None:
        await self._session.execute(update(PostOrm).where(PostOrm.id == post.id).values(active=post.active))

    async def get(self, id: int) -> PostOrm | None:
        result = await self._session.execute(select(PostOrm).where(PostOrm.id == id))

        post = result.scalar()
        return post

    async def get_with_tags(self, id: int) -> PostWithTags | None:
        result = await self._session.execute(
            select(PostOrm)
            .options(selectinload(PostOrm.tags).selectinload(PostTagOrm.tag))
            .where(PostOrm.id == id)
            .distinct()
        )

        post = result.scalar()
        return from_orm_to_post_with_tags(post) if post else None

    async def all_ids(self) -> list[int]:
        results = await self._session.execute(select(PostOrm.id))

        ids = results.scalars().all()
        return ids

    async def bulk_save(self, batch: list[ParsedPostDTO]) -> list[Post]:
        records = []
        for r in batch:
            records.append(asdict(r))

        posts = []
        for post in batch:
            posts.append(
                PostOrm(
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
            )

        self._session.add_all(posts)
        await self._session.flush()

        return posts
