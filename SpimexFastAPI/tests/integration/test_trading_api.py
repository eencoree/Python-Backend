import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_dates_endpoint(test_app, client):
    response = await client.get("/api/v1/trading/dates")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["dates"], list)
    assert len(data) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_results_endpoint(test_app, client):
    response = await client.get(
        "/api/v1/trading/results",
        params={"limit": 10}
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["oil_id"] == "A1"
    assert data[0]["volume"] == 100


@pytest.mark.integration
@pytest.mark.parametrize(
    "limit,status",
    [
        (10, 200),
        (1, 200),
        (-1, 422),
        ("abc", 422),
    ]
)
@pytest.mark.asyncio
async def test_results_limit_validation(client, limit, status):
    response = await client.get(
        "/api/v1/trading/results",
        params={"limit": limit}
    )

    assert response.status_code == status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_dynamics_endpoint(test_app, client):
    response = await client.get(
        "/api/v1/trading/dynamics",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-10"
        }
    )

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_dynamics_missing_start_date(test_app, client):
    response = await client.get(
        "/api/v1/trading/dynamics",
        params={
            "end_date": "2024-01-10"
        }
    )

    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_dynamics_invalid_date(test_app, client):
    response = await client.get(
        "/api/v1/trading/dynamics",
        params={
            "start_date": "invalid date",
            "end_date": "2024-01-10"
        }
    )

    assert response.status_code == 422
