from sqlalchemy import exists, select, update
from sqlalchemy.orm import joinedload

from posts.dto.post import PostWithTags
from posts.persistence.data_mappers.base import BaseDataMapper
from posts.persistence.mappers.post_with_tags import from_orm_to_post_with_tags
from posts.persistence.models import PostOrm, PostTagOrm, SiteOrm, SitePostOrm


class SitePostDataMapper(BaseDataMapper):
    async def all_sites(self) -> list[SiteOrm]:
        result = await self._session.execute(select(SiteOrm))
        return result.scalars().all()

    async def filter_sites(self, ids: list[int]) -> list[SiteOrm]:
        result = await self._session.execute(select(SiteOrm).where(SiteOrm.id.in_(ids)))
        return result.scalars().all()

    async def get_site(self, id: int) -> SiteOrm:
        result = await self._session.get(SiteOrm, id)
        return result

    async def change_sended(self, site_id: int, post_ids: list[int], sended: bool = True) -> None:
        await self._session.execute(
            update(SitePostOrm)
            .where(SitePostOrm.post_id.in_(post_ids), SitePostOrm.site_id == site_id)
            .values(sended=sended)
        )

    async def bulk_create_site_posts_relation(self, site_id: int, posts: list[PostWithTags]) -> None:
        relations = [SitePostOrm(site_id=site_id, post_id=post.id) for post in posts]
        self._session.add_all(relations)

    async def filter_posts_without_site(self, site_id: int, active: bool = True) -> list[PostWithTags]:
        subq = select(SitePostOrm.id).where(SitePostOrm.post_id == PostOrm.id, SitePostOrm.site_id == site_id)

        stmt = (
            select(PostOrm)
            .options(joinedload(PostOrm.tags).joinedload(PostTagOrm.tag), joinedload(PostOrm.siteposts))
            .where(~exists(subq), PostOrm.active == active)
            .distinct()
        )

        results = await self._session.execute(stmt)
        posts = results.scalars().unique()

        return [from_orm_to_post_with_tags(post) for post in posts]

    async def filter_posts(self, site_id: int, sended: bool = False, active: bool = True) -> list[PostWithTags]:
        results = await self._session.execute(
            select(PostOrm)
            .join(PostOrm.siteposts)
            .options(joinedload(PostOrm.tags).joinedload(PostTagOrm.tag), joinedload(PostOrm.siteposts))
            .where(SitePostOrm.site_id == site_id, SitePostOrm.sended == sended, PostOrm.active == active)
            .distinct()
        )

        posts = results.scalars().unique()
        return [from_orm_to_post_with_tags(post) for post in posts]
