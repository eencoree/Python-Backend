from datetime import date

import pytest

from src.links import parse_page_links

HTML = """
<a href="/files/trades/result/pdf/oil/oil_20260424162000.pdf"></a>
"""


class FakeResponse:
    def __init__(self, text):
        self._text = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def text(self):
        return HTML

    def raise_for_status(self):
        pass


class FakeSession:
    def get(self, url, timeout=None):
        return FakeResponse(HTML)


@pytest.mark.asyncio
async def test_parse_page_links():
    session = FakeSession()

    result = [
        item async for item in parse_page_links(
            session,
            "https://spimex.com/markets/oil_products/trades/results/",
            date(2026, 4, 23),
            date(2026, 4, 25),
        )
    ]

    assert len(result) == 1
    assert result[0][0].startswith("https://spimex.com")
