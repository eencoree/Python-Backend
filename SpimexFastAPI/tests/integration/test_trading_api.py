import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_get_dates_endpoint(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/trading/dates")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_results_endpoint(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/trading/results",
            params={"limit": 10}
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_dynamics_endpoint(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/trading/dynamics",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-10"
            }
        )

    assert response.status_code == 200
