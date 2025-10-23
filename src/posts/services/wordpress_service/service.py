import json
import sys
import traceback
from dataclasses import asdict
from urllib.parse import unquote

import httpx
from redis import Redis  # type: ignore

from posts.dto.operation_result import OperationResult
from posts.dto.post import Post, Tag
from posts.dto.site import Site
from posts.dto.wordpress_post import WordpressPostDTO


class WordpressService:
    def __init__(self, session: httpx.AsyncClient, redis: Redis, cache_key: str = "wp_access_tokens") -> None:
        self._session = session
        self._redis = redis
        self._access_tokens: dict[str, str] = dict()
        self._cache_key = cache_key

    async def fetch_access_token(self, site: Site) -> str:
        async with httpx.AsyncClient() as session:
            response = await session.post(
                f"{site.address}/wp-json/jwt-auth/v1/token", json={"username": site.username, "password": site.password}
            )
            data = response.json()

            return data["token"]

    async def get_access_token(self, site: Site) -> str:
        cached_token = self._access_tokens.get(site.address)
        if cached_token:
            return cached_token

        cache_tokens = json.loads(self._redis.get(self._cache_key)) if self._redis.get(self._cache_key) else None
        if cache_tokens is None or (cache_tokens and site.address not in cache_tokens):
            access_token = await self.fetch_access_token(site)
            self._access_tokens[site.address] = access_token
            cache_tokens = cache_tokens | {site.address: access_token} if cache_tokens else {site.address: access_token}
            self._redis.set(self._cache_key, json.dumps(cache_tokens), ex=60 * 5)

            return access_token

        return cache_tokens[site.address]

    async def all_tags(self, site: Site) -> list[Tag]:
        async with httpx.AsyncClient(timeout=30) as session:
            tags = []
            page = 1
            while True:
                response = await session.get(f"{site.address}/wp-json/wp/v2/tags?per_page=100&page={page}")
                page += 1
                data = response.json()
                if not data:
                    return tags
                tags.extend(
                    [Tag(id=json_tag["id"], name=json_tag["name"], slug=unquote(json_tag["slug"])) for json_tag in data]
                )

    async def get_post_by_slug(self, site: Site, slug: str) -> Post:
        async with httpx.AsyncClient() as session:
            response = await session.get(f"{site.address}/wp-json/wp/v2/posts?slug={slug}")
            data = response.json()

            if not data:
                return None
            post = data[0]
            return Post(
                id=post["id"],
                title=post["title"],
                description="",
                published=post["date"],
                h1="",
                image="",
                content="",
                content2="",
                slug="",
                active=post["status"],
            )

    async def delete_post(self, site: Site, post_id: int, access_token: str) -> None:
        async with httpx.AsyncClient() as session:
            await session.delete(
                f"{site.address}/wp-json/wp/v2/posts/{post_id}",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"},
            )

    async def send_tag(self, site: Site, tag: Tag, access_token: str) -> OperationResult:
        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    f"{site.address}/wp-json/wp/v2/tags",
                    json=asdict(tag),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"},
                )

                data = response.json()

                if response.status_code == 201:
                    return OperationResult(
                        success=True, data=Tag(id=data["id"], slug=unquote(data["slug"]), name=data["name"])
                    )

                error_message = json.dumps(data, indent=2, ensure_ascii=False)

                return OperationResult(success=False, error_message=f"Лог ошибки с сайта Wordpress: {error_message}")
        except Exception as e:
            type, value, tb = sys.exc_info()
            traceback_str = "".join(traceback.format_exception(type, value, tb))

            return OperationResult(success=False, error_message=f"Ошибка сервера: {traceback_str}")

    async def send_post_image(self, site: Site, image_name: str, image: bytes, access_token: str) -> int:
        async with httpx.AsyncClient() as session:
            upload_response = await session.post(
                f"{site.address}/wp-json/wp/v2/media",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": (image_name, image, "image/jpeg")},
            )

            return upload_response.json()["id"]

    async def send_post(self, site: Site, post: WordpressPostDTO, access_token: str) -> OperationResult:
        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    f"{site.address}/wp-json/wp/v2/posts",
                    json=asdict(post),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"},
                )

                if response.status_code == 201:
                    return OperationResult(success=True)

                data = response.json()
                error_message = json.dumps(data, indent=2, ensure_ascii=False)

                return OperationResult(success=False, error_message=f"Лог ошибки с сайта Wordpress: {error_message}")
        except Exception as e:
            type, value, tb = sys.exc_info()
            traceback_str = "".join(traceback.format_exception(type, value, tb))

            return OperationResult(success=False, error_message=f"Ошибка сервера: {traceback_str}")
