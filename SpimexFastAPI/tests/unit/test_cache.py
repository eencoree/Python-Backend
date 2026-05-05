import pytest
from unittest.mock import AsyncMock

from app.cache import CacheService


@pytest.mark.asyncio
async def test_cache_hit():
    redis = AsyncMock()

    redis.get.return_value = '{"data": 123}'

    cache = CacheService(redis)

    result = await cache.get("key")

    assert result == {"data": 123}
    redis.get.assert_called_once()