from datetime import date

import pytest
from asgi_lifespan import LifespanManager

from app.main import app
from app.services import TradingService


def fake_item():
    return {
        "id": 10,
        "date": date(2024, 1, 1),
        "oil_id": "A1",
        "delivery_type_id": "T1",
        "delivery_basis_id": "B1",
        "volume": 100,
        "total": 1000,
        "count": 5,
    }

@pytest.fixture
def fixture_item():
    return fake_item()

class FakeRepository:
    async def get_last_trading_dates(self, *args, **kwargs):
        return [fake_item()["date"]]

    async def get_trading_results(self, *args, **kwargs):
        return [fake_item()]

    async def get_dynamics(self, *args, **kwargs):
        return [fake_item()]


class FakeCache:
    def __init__(self):
        self.storage = {}

    async def get(self, key):
        return self.storage.get(key)

    async def set(self, key, value):
        self.storage[key] = value


@pytest.fixture
async def test_app():
    async with LifespanManager(app):
        app.state.trading_service = TradingService(
            repository=FakeRepository(),
            cache=FakeCache()
        )
        yield app
