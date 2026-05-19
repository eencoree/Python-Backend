from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.schemas import TradingResultResponse, DynamicsResponse
from app.services import TradingService


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_trading_results_repository_error():
    repository = AsyncMock()
    cache = AsyncMock()

    cache.get.return_value = None
    repository.get_trading_results.side_effect = Exception("DB error")

    service = TradingService(repository, cache)

    with pytest.raises(Exception):
        await service.get_trading_results(
            session=None,
            oil_id=None,
            delivery_type_id=None,
            delivery_basis_id=None,
            limit=10
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_dynamics(fixture_item):
    repository = AsyncMock()
    cache = AsyncMock()

    cache.get.return_value = None
    repository.get_dynamics.return_value = [fixture_item]

    service = TradingService(repository, cache)

    result = await service.get_dynamics(
        session=None,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
        oil_id=None,
        delivery_type_id=None,
        delivery_basis_id=None
    )

    assert result == [DynamicsResponse(**fixture_item).model_dump()]

    repository.get_dynamics.assert_called_once()


@pytest.mark.unit
def test_trading_result_serialization(fixture_item):
    model = TradingResultResponse(**fixture_item)

    result = model.model_dump()

    assert result["oil_id"] == "A1"


@pytest.mark.unit
def test_make_cache_key():
    params1 = {"oil_id": "A1"}
    params2 = {"oil_id": "A2"}
    result1 = TradingService.make_cache_key("trading", params1)
    result1_2 = TradingService.make_cache_key("trading", params1)

    assert result1 == result1_2
    result2 = TradingService.make_cache_key("trading", params2)

    assert result1 != result2