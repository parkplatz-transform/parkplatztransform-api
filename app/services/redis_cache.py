from typing import Optional
from app.config import settings

from aioredis import Redis, create_redis_pool


class RedisCache:
    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def init_cache(self):
        self.redis_cache = await create_redis_pool(
            f"{settings.redis_url}?encoding=utf-8"
        )

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value, expires: int):
        return await self.redis_cache.set(key, value, expire=expires)

    async def get(self, key):
        return await self.redis_cache.get(key)

    async def delete(self, key):
        return await self.redis_cache.delete(key)

    async def close(self):
        self.redis_cache.close()
        await self.redis_cache.wait_closed()


redis_cache = RedisCache()
