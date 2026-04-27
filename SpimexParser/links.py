import enum
import logging
import ssl
import urllib
from datetime import date, datetime
from typing import Generator, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
FILE_EXTENSIONS = (".pdf", ".xls")
DEFAULT_URL: str = "https://spimex.com"


class Prefix(enum.StrEnum):
    PDF = "/files/trades/result/pdf/oil/oil_"
    XLS = "/files/trades/result/oil_xls/oil_xls_"


def iterate_pages(base_url: str) -> Generator[str, None, None]:
    """
    Итерируется по страницам на сайте и возвращает генератор-объект soup с конкретного HTML
    """
    page = 1

    while True:
        logger.info(f"Парсинг файлов на странице {page}")
        url = f"{base_url}?page=page-{page}"
        html = get_safe_html(url)
        soup = BeautifulSoup(html, "html.parser")

        yield soup

        next_link = soup.find("a", string=str(page + 1))
        if not next_link:
            break

        page += 1


def parse_page_links(url: str, start_date: date, end_date: date) -> Generator[tuple, None, None]:
    """
    Парсит ссылки на бюллетени с нескольких HTML страниц:
    :param url: url ссылка
    :param start_date: дата начала периода поиска
    :param end_date: дата конца периода поиска
    :return: генератор из пар (url, дата)
    """

    for soup in iterate_pages(url):

        for href in get_valid_links(soup):
            file_date = get_date(href)

            if not file_date:
                continue

            if file_date < start_date:
                logger.info("Достигнут предел по дате, остановка")
                return

            if start_date <= file_date <= end_date:
                yield get_url(href), file_date


def get_safe_html(url: str):
    context = ssl.create_default_context()
    try:
        logger.info(f"Скачивание HTML: {url}")
        with urllib.request.urlopen(url, context=context) as response:
            html = response.read()
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {url}", exc_info=e)
        raise
    return html


def get_valid_links(soup: BeautifulSoup) -> Generator[str, None, None]:
    """
    Выделяет ссылку, фильтрует по префиксу и расширению из списка найденных ссылок.
    :returns Генератор, возвращающий по одной ссылке
    """
    logger.info(f"Поиск всех ссылок на файлы")

    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue
        href_wo_params = href.split("?")[0]

        if href_wo_params.endswith(FILE_EXTENSIONS) \
                and any(prefix in href for prefix in Prefix):
            yield href


def get_date(href: str) -> Optional[date]:
    """
    Выделяет дату из ссылки
    :param href: ссылка
    :return: дата или None если дата не найдена
    """
    try:
        for prefix in Prefix:
            if prefix in href:
                date_str = href.split(prefix)[1][:8]
                return datetime.strptime(date_str, "%Y%m%d").date()
    except (IndexError, ValueError) as e:
        logger.warning(f"Ошибка при извлечении даты из {href}", exc_info=e)

    return None


def get_url(href: str) -> str:
    """
    Собирает полный url из ссылки, добавляя базовый префикс, если адрес в ссылке не найден
    :param href: ссылка
    :return: url
    """
    return href if href.startswith("http") else f"{DEFAULT_URL}{href}"
