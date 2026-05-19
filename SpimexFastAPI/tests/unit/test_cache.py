from unittest.mock import AsyncMock

import pytest

from app.cache import CacheService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_set():
    redis = AsyncMock()

    cache = CacheService(redis)

    data = {"test": 123}

    await cache.set("key", data)

    redis.set.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_hit():
    redis = AsyncMock()

    redis.get.return_value = '{"data": 123}'

    cache = CacheService(redis)

    result = await cache.get("key")

    assert result == {"data": 123}
    redis.get.assert_called_once()
