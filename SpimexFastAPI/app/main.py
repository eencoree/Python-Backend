from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.v1.routers import trading_router, health_router
from app.cache import CacheService
from app.cache.redis import RedisClient
from app.core.middleware import LoggingMiddleware
from app.repositories import TradingRepository
from app.services import TradingService
from app.core import db_helper
from app.core import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis_client = RedisClient(settings.redis.url)
    app.state.trading_service = TradingService(
        repository=TradingRepository(),
        cache=CacheService(redis_client),
    )
    yield
    await db_helper.dispose()
    await redis_client.client.aclose()


app = FastAPI(lifespan=lifespan)
app.middleware("http")(LoggingMiddleware())
settings = get_settings()
app.include_router(
    trading_router,
    prefix=settings.api.prefix
)
app.include_router(
    health_router,
    prefix=settings.api.prefix
)
