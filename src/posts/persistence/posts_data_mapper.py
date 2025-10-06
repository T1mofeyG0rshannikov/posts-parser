from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from posts.persistence.models import PostOrm, PostTagOrm
from posts.usecases.posts.parsing.dto import ParsedPostDTO


class PostDataMapper:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, post: PostOrm) -> None:
        self._session.refresh(post)

    async def get(self, id: int) -> PostOrm | None:
        result = await self._session.execute(select(PostOrm).where(PostOrm.id == id))

        post = result.scalar()
        return post

    async def all_ids(self) -> list[int]:
        results = await self._session.execute(select(PostOrm.id))

        ids = results.scalars().all()
        return ids

    async def bulk_save(self, batch: list[ParsedPostDTO]) -> None:
        # try:
        records = []
        for r in batch:
            records.append(asdict(r))

        print(len(batch), "B batch")
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

        print(len(batch), "B batch 2")
        self._session.add_all(posts)
        print(len(batch), "B batch 3")
        await self._session.flush()
        print(len(batch), "B batch 4")

        tags = []
        for b, post in zip(batch, posts):
            tags.extend([PostTagOrm(post_id=post.id, name=tag.name, slug=tag.slug) for tag in b.tags])
        print(len(batch), "B batch 5")

        self._session.add_all(tags)
        print(len(batch), "B batch 6")
        print(len(batch), "B batch 7")
        print("Flushed batch %d", len(records))
        print(len(batch), "B batch 8")
        # except Exception as e:
        # print(e)
        # await session.rollback()
