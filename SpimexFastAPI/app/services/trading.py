import hashlib
import json
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheService
from app.repositories import TradingRepository
from app.schemas import TradingResultResponse


class TradingService:
    def __init__(
            self,
            repository: TradingRepository,
            cache: CacheService,
    ):
        self.repository = repository
        self.cache = cache

    async def get_last_trading_dates(
            self,
            session: AsyncSession,
            last_days: int
    ):
        key = f"trading:dates:{last_days}"
        cached = await self.cache.get(key)
        if cached:
            return cached

        dates = await self.repository.get_last_trading_dates(last_days, session)
        await self.cache.set(key, dates)
        return dates

    async def get_trading_results(
            self,
            session: AsyncSession,
            oil_id: str | None,
            delivery_type_id: str | None,
            delivery_basis_id: str | None,
            limit: int,
    ):
        key = f"trading:results:{oil_id}:{delivery_type_id}:{delivery_basis_id}:{limit}"

        cached = await self.cache.get(key)
        if cached:
            return cached

        data = await self.repository.get_trading_results(
            session,
            oil_id,
            delivery_type_id,
            delivery_basis_id,
            limit,
        )
        data = [TradingResultResponse.model_validate(obj).model_dump() for obj in data]
        await self.cache.set(key, data)
        return data

    @staticmethod
    def make_cache_key(prefix: str, params: dict):
        raw = json.dumps(params, sort_keys=True)
        hashed = hashlib.md5(raw.encode()).hexdigest()
        return f"{prefix}:{hashed}"

    async def get_dynamics(
            self,
            session: AsyncSession,
            start_date: date,
            end_date: date,
            oil_id: str | None,
            delivery_type_id: str | None,
            delivery_basis_id: str | None,
    ):
        params = {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "oil_id": oil_id,
            "delivery_type_id": delivery_type_id,
            "delivery_basis_id": delivery_basis_id,
        }

        key = self.make_cache_key("trading:dynamics", params)

        cached = await self.cache.get(key)
        if cached:
            return cached

        data = await self.repository.get_dynamics(
            session,
            start_date,
            end_date,
            oil_id,
            delivery_type_id,
            delivery_basis_id,
        )
        data = [TradingResultResponse.model_validate(obj).model_dump() for obj in data]
        await self.cache.set(key, data)
        return data