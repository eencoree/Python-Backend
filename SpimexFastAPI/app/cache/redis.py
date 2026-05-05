import redis.asyncio as redis


class RedisClient:
    def __init__(self, url: str):
        self.client = redis.from_url(url, decode_responses=True)

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        await self.client.set(key, value, ex=ttl)

    async def flush(self):
        await self.client.flushall()
