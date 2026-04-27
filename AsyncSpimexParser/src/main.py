import asyncio
import logging
import time
from datetime import date

import aiohttp

from src.database import AsyncSessionLocal
from src.extract import (
    extract_pdf,
    extract_xls,
    clean_df,
)
from src.links import parse_page_links
from src.load import load_to_db
from src.transform import transform_df

URL = "https://spimex.com/markets/oil_products/trades/results/"
TB_NAME = "Единица измерения: Метрическая тонна"

logger = logging.getLogger(__name__)


def get_file_type(url: str) -> str:
    url = url.split("?")[0]

    if url.endswith(".pdf"):
        return "pdf"

    if url.endswith(".xls") or url.endswith(".xlsx"):
        return "xls"

    return "unknown"


async def process_file(
        file_url: str,
        file_date: date,
        http_session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
):
    """
    Реализует ETL процесс
    """

    async with semaphore:
        try:
            file_type = get_file_type(file_url)

            if file_type == "pdf":
                df = await extract_pdf(
                    http_session,
                    file_url,
                    TB_NAME,
                )

            elif file_type == "xls":
                df = await extract_xls(
                    http_session,
                    file_url,
                    TB_NAME,
                )

            else:
                logger.warning(
                    f"[ETL] Неизвестный формат: {file_url}"
                )
                return None, file_url, file_date

            if df is None or df.empty:
                return None, file_url, file_date

            df = await asyncio.to_thread(clean_df, df)

            df = await asyncio.to_thread(
                transform_df,
                df,
                file_date
            )

            return df, file_url, file_date

        except Exception as e:
            logger.error(
                f"[ETL] Ошибка обработки {file_url}",
                exc_info=e
            )
            return None, file_url, file_date


async def run_etl_async(
        concurrency: int = 5,
        files_to_process=None,
        start_date=date(2026, 4, 1),
        end_date=date.today(),
):
    start_total = time.perf_counter()

    total_rows = 0
    failed_files = []
    timeout = aiohttp.ClientTimeout(total=60)

    connector = aiohttp.TCPConnector(limit=concurrency)

    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": "Mozilla/5.0"},
    ) as http_session:

        if files_to_process is None:
            files = [
                item async for item in parse_page_links(
                    http_session,
                    URL,
                    start_date,
                    end_date,
                )
            ]
        else:
            files = files_to_process

        logger.info(f"[ETL] Найдено файлов: {len(files)}")

        tasks = [
            process_file(
                file_url,
                file_date,
                http_session,
                semaphore
            )
            for file_url, file_date in files
        ]

        async with AsyncSessionLocal() as db_session:

            for task in asyncio.as_completed(tasks):

                df, file_url, file_date = await task

                if df is None:
                    failed_files.append((file_url, file_date))
                    continue

                try:
                    rows = len(df)
                    total_rows += rows

                    await load_to_db(
                        db_session,
                        df
                    )

                except Exception as e:
                    logger.error(
                        f"[DB] Ошибка вставки {file_url}",
                        exc_info=e
                    )
                    failed_files.append((file_url, file_date))

    total_time = time.perf_counter() - start_total

    logger.info(
        f"[ETL] Готово: {total_rows} строк "
        f"за {total_time:.2f} сек"
    )

    if failed_files:
        logger.warning(
            f"[ETL] Не удалось обработать "
            f"{len(failed_files)} файлов"
        )

    return failed_files


async def main():
    failed_files = await run_etl_async(concurrency=5)

    retries = 2

    while failed_files and retries > 0:
        logger.info(
            f"[ETL] Повторная обработка "
            f"{len(failed_files)} файлов"
        )

        failed_files = await run_etl_async(concurrency=3, files_to_process=failed_files)

        retries -= 1


if __name__ == "__main__":
    asyncio.run(main())
