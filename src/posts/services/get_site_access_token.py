import json

from aioredis import Redis

from posts.dto.site import Site
from posts.services.wordpress_service.service import WordpressService


class GetSiteAccessToken:
    def __init__(self, wordpress_service: WordpressService, redis: Redis, cache_key: str = "wp_access_tokens") -> None:
        self._wordpress_service = wordpress_service
        self._redis = redis
        self._access_tokens: dict[str, str] = dict()
        self._cache_key = cache_key

    async def __call__(self, site: Site) -> str:
        cached_token = self._access_tokens.get(site.address)
        if cached_token:
            return cached_token

        cache_tokens = json.loads(self._redis.get(self._cache_key)) if self._redis.get(self._cache_key) else None
        if cache_tokens is None or (cache_tokens and site.address not in cache_tokens):
            access_token = await self._wordpress_service.fetch_access_token(site)
            self._access_tokens[site.address] = access_token
            cache_tokens = cache_tokens | {site.address: access_token} if cache_tokens else {site.address: access_token}
            self._redis.set(self._cache_key, json.dumps(cache_tokens), ex=60 * 5)

            return access_token

        return cache_tokens[site.address]
