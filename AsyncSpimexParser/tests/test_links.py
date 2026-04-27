from datetime import date

import aiohttp
import pytest
from aioresponses import aioresponses
from bs4 import BeautifulSoup

from src.links import get_date, get_url, get_valid_links, get_safe_html

HTML = """
<a href="/files/trades/result/pdf/oil/oil_20260424162000.pdf"></a>
<a href="/other/file.txt"></a>
"""


def test_get_date_pdf():
    href = "/files/trades/result/pdf/oil/oil_20260424162000.pdf"
    assert get_date(href) == date(2026, 4, 24)


def test_get_date_invalid():
    assert get_date("bad_link") is None


def test_get_url_relative():
    assert get_url("/files/test.pdf").startswith("https://spimex.com")


def test_get_url_absolute():
    url = "https://spimex.com/file.pdf"
    assert get_url(url) == url


def test_get_valid_links():
    soup = BeautifulSoup(HTML, "html.parser")
    links = list(get_valid_links(soup))

    assert len(links) == 1
    assert "oil_20260424" in links[0]


@pytest.mark.asyncio
async def test_get_safe_html():
    url = "https://test.com"

    with aioresponses() as m:
        m.get(url, body="<html></html>")

        async with aiohttp.ClientSession() as session:
            html = await get_safe_html(session, url)

    assert "<html" in html
