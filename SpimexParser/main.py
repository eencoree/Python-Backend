import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from time import sleep

import requests
from requests.adapters import HTTPAdapter, Retry

from database import Session, create_tables
from extract import pdf_generator, extract_target_page_tables, tables_to_dataframe, clean_df, extract_xls
from links import parse_page_links
from load import load_to_db
from logger_config import setup_logging
from transform import transform_df

setup_logging()
URL = "https://spimex.com/markets/oil_products/trades/results/"
TB_NAME = "Единица измерения: Метрическая тонна"
logger = logging.getLogger(__name__)


def get_file_type(url: str) -> str:
    url = url.split("?")[0]
    if url.endswith(".pdf"):
        return "pdf"
    elif url.endswith(".xls") or url.endswith(".xlsx"):
        return "xls"
    else:
        return "unknown"


def get_session_with_retries(total_retries=5, backoff_factor=1, timeout=30):
    session = requests.Session()
    retries = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.timeout = timeout
    return session


def process_file(file_url: str, file_date: date, max_attempts=3):
    """Скачивание, парсинг, чистка и трансформация"""
    file_type = get_file_type(file_url)
    try:
        if file_type == "pdf":
            with pdf_generator(file_url) as pages:
                all_tables = []
                for page in pages:
                    tables = extract_target_page_tables(page, TB_NAME)
                    all_tables.extend(tables)
            if not all_tables:
                logger.warning(f"[ETL] Нет таблиц в PDF: {file_url}")
                return None
            df = tables_to_dataframe(all_tables)

        elif file_type == "xls":
            session = get_session_with_retries()
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"[ETL] Скачивание {file_url} (попытка {attempt})")
                    df = extract_xls(file_url, TB_NAME, session=session)
                    break
                except Exception as e:
                    logger.warning(f"[ETL] Ошибка при скачивании {file_url}: {e}")
                    if attempt < max_attempts:
                        sleep(2 ** attempt)
                    else:
                        raise
        else:
            logger.error(f"[ETL] Неизвестный формат: {file_url}")
            return None

        if df.empty:
            return None

        df = clean_df(df)
        df = transform_df(df, file_date)
        return df

    except Exception as e:
        logger.error(f"[ETL] Ошибка при обработке {file_url}", exc_info=e)
        return None


def run_etl_parallel(max_workers=5):
    start_total = time.perf_counter()
    total_rows = 0
    failed_files = []

    # Собираем сначала все ссылки
    files = list(parse_page_links(URL, date(2023, 1, 1), date.today()))
    logger.info(f"[ETL] Найдено {len(files)} файлов для обработки")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_file, file_url, file_date): (file_url, file_date)
            for file_url, file_date in files
        }

        with Session() as session:
            for future in as_completed(future_to_file):
                file_url, file_date = future_to_file[future]
                try:
                    df = future.result()
                    if df is None:
                        failed_files.append((file_url, file_date))
                        continue

                    rows = len(df)
                    total_rows += rows
                    load_to_db(session, df)

                except Exception as e:
                    logger.error(f"[ETL] Ошибка при вставке/обработке {file_url}", exc_info=e)
                    failed_files.append((file_url, file_date))

    total_time = time.perf_counter() - start_total
    logger.info(f"[ETL] Готово: {total_rows} строк за {total_time:.2f} сек")
    if failed_files:
        logger.warning(f"[ETL] Не удалось обработать {len(failed_files)} файлов, их можно повторить")
    return failed_files


if __name__ == "__main__":
    create_tables()
    failed_files = run_etl_parallel(max_workers=5)

    # Повтор обработки пропущенных файлов
    retries = 2
    while failed_files and retries > 0:
        logger.info(f"[ETL] Повторная обработка {len(failed_files)} пропущенных файлов")
        failed_files = run_etl_parallel(max_workers=3)
        retries -= 1
