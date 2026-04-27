import pytest

from src.main import run_etl_async


@pytest.mark.asyncio
async def test_run_etl_empty(monkeypatch):
    async def fake_parse(*args, **kwargs):
        return
        yield

    monkeypatch.setattr("src.main.parse_page_links", fake_parse)

    result = await run_etl_async(
        concurrency=1,
    )

    assert result == []
