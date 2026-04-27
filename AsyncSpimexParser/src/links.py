import enum
import logging
from datetime import date, datetime
from typing import Generator, Optional, AsyncGenerator

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
FILE_EXTENSIONS = (".pdf", ".xls")
DEFAULT_URL: str = "https://spimex.com"


class Prefix(enum.StrEnum):
    PDF = "/files/trades/result/pdf/oil/oil_"
    XLS = "/files/trades/result/oil_xls/oil_xls_"


async def get_safe_html(session: aiohttp.ClientSession, url: str) -> str:
    """
    Асинхронно скачивает html страницы
    """
    try:
        logger.info(f"[LINKS] Скачивание HTML: {url}")

        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            return await response.text()

    except Exception as e:
        logger.error(f"[LINKS] Ошибка при чтении файла {url}", exc_info=e)
        raise


async def iterate_pages(
        session: aiohttp.ClientSession,
        base_url: str
) -> AsyncGenerator[BeautifulSoup, None]:
    """
    Асинхронно итерируется по страницам на сайте и возвращает генератор-объект soup с конкретного HTML
    """
    page = 1

    while True:
        logger.info(f"[LINKS] Парсинг файлов на странице {page}")
        url = f"{base_url}?page=page-{page}"
        html = await get_safe_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        yield soup

        next_link = soup.find("a", string=str(page + 1))
        if not next_link:
            logger.info("[LINKS] Последняя страница достигнута")
            break

        page += 1


async def parse_page_links(
        session: aiohttp.ClientSession,
        url: str,
        start_date: date,
        end_date: date
) -> AsyncGenerator[tuple[str, date], None]:
    """
    Собирает ссылки на файлы за указанный диапазон дат
    """

    async for soup in iterate_pages(session, url):

        for href in get_valid_links(soup):
            file_date = get_date(href)

            if not file_date:
                continue

            if file_date < start_date:
                logger.info("[LINKS] Достигнут предел по дате")
                return

            if start_date <= file_date <= end_date:
                yield get_url(href), file_date


def get_valid_links(soup: BeautifulSoup) -> Generator[str, None, None]:
    logger.info(f"[LINKS] Поиск всех ссылок на файлы")

    for link in soup.find_all("a"):
        href = link.get("href")

        if not href:
            continue

        if not isinstance(href, str):
            continue

        href_wo_params = href.split("?")[0]

        if href_wo_params.endswith(FILE_EXTENSIONS) and any(href.startswith(p.value) for p in Prefix):
            yield href


def get_date(href: str) -> Optional[date]:
    """
    Выделяет дату из ссылки
    """
    try:
        for prefix in Prefix:
            if prefix in href:
                date_str = href.split(prefix)[1][:8]
                return datetime.strptime(date_str, "%Y%m%d").date()

    except (IndexError, ValueError) as e:
        logger.warning(f"[LINKS] Ошибка при извлечении даты из {href}", exc_info=e)

    return None


def get_url(href: str) -> str:
    """
    Собирает полный url из ссылки, добавляя базовый префикс, если адрес в ссылке не найден
    """
    return href if href.startswith("http") else f"{DEFAULT_URL}{href}"
