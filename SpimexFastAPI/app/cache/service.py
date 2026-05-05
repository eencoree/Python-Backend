import json
import logging

from app.cache.redis import RedisClient
from app.cache.utils import get_ttl_until_14_11

logger = logging.getLogger("cache")

class CacheService:
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client

    async def get(self, key):
        data = await self.redis.get(key)
        if data:
            logger.info(f"CACHE HIT: {key}")
            return json.loads(data)

        logger.info(f"CACHE MISS: {key}")
        return None

    async def set(self, key, value):
        ttl = get_ttl_until_14_11()
        await self.redis.set(
            key,
            json.dumps(value, default=str),
            ttl=ttl
        )
