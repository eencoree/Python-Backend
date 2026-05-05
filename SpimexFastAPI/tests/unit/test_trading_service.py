from unittest.mock import AsyncMock

import pytest

from app.schemas import TradingResultResponse, DynamicsResponse
from app.services import TradingService


@pytest.mark.asyncio
async def test_get_last_trading_dates_cache_miss():
    repository = AsyncMock()
    cache = AsyncMock()

    cache.get.return_value = None
    repository.get_last_trading_dates.return_value = ["2024-01-01"]

    service = TradingService(repository, cache)

    result = await service.get_last_trading_dates(
        session=None,
        last_days=30
    )

    assert result == ["2024-01-01"]

    cache.get.assert_called_once()
    repository.get_last_trading_dates.assert_called_once()
    cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_last_trading_dates_cache_hit():
    repository = AsyncMock()
    cache = AsyncMock()

    cache.get.return_value = ["2024-01-01"]

    service = TradingService(repository, cache)

    result = await service.get_last_trading_dates(
        session=None,
        last_days=30
    )

    assert result == ["2024-01-01"]

    repository.get_last_trading_dates.assert_not_called()


@pytest.mark.asyncio
async def test_get_trading_results(fixture_item):
    repository = AsyncMock()
    cache = AsyncMock()

    cache.get.return_value = None
    repository.get_trading_results.return_value = [fixture_item]

    service = TradingService(repository, cache)

    result = await service.get_trading_results(
        session=None,
        oil_id="A1",
        delivery_type_id=None,
        delivery_basis_id=None,
        limit=100
    )

    assert result == [TradingResultResponse(**fixture_item).model_dump()]

    repository.get_trading_results.assert_called_once()


@pytest.mark.asyncio
async def test_get_dynamics(fixture_item):
    repository = AsyncMock()
    cache = AsyncMock()

    cache.get.return_value = None
    repository.get_dynamics.return_value = [fixture_item]

    service = TradingService(repository, cache)

    result = await service.get_dynamics(
        session=None,
        start_date="2024-01-01",
        end_date="2024-01-10",
        oil_id=None,
        delivery_type_id=None,
        delivery_basis_id=None
    )

    assert result == [DynamicsResponse(**fixture_item).model_dump()]

    repository.get_dynamics.assert_called_once()
