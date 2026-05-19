import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac