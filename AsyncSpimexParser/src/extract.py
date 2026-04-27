import asyncio
import io
import logging
import re
from typing import List

import aiohttp
import pandas as pd
import pdfplumber

logger = logging.getLogger(__name__)


async def download_bytes(
        session: aiohttp.ClientSession,
        url: str,
        retries: int = 3
) -> bytes:
    """
    Универсальное асинхронное скачивание файла в bytes
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"[EXTRACT] Скачивание {url} (попытка {attempt})")

            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()

        except aiohttp.ClientResponseError as e:
            logger.warning(f"[EXTRACT] Ошибка скачивания {url} (попытка {attempt}): {e}")
            if attempt < retries:
                await asyncio.sleep(2)

    logger.error(f"[EXTRACT] Не удалось скачать {url} после {retries} попыток")
    raise RuntimeError(f"Не удалось скачать файл: {url}")


async def extract_pdf(
        session: aiohttp.ClientSession,
        url: str,
        tb_name: str
) -> pd.DataFrame:
    """
    Асинхронная загрузка PDF + синхронный parsing через thread
    """
    pdf_bytes = await download_bytes(session, url)

    return await asyncio.to_thread(
        parse_pdf_bytes,
        pdf_bytes,
        tb_name
    )


def parse_pdf_bytes(pdf_bytes: bytes, tb_name: str) -> pd.DataFrame:
    """
    Синхронный CPU-bound parsing PDF
    """
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        all_tables = []

        for page in pdf.pages:
            tables = extract_target_page_tables(page, tb_name)
            all_tables.extend(tables)

    if not all_tables:
        return pd.DataFrame()

    return tables_to_dataframe(all_tables)


async def extract_xls(
        session: aiohttp.ClientSession,
        url: str,
        tb_name: str
) -> pd.DataFrame:
    """
    Асинхронная загрузка xls + parsing в thread
    """
    file_bytes = await download_bytes(session, url)
    try:
        df = await asyncio.to_thread(
            parse_xls_bytes,
            file_bytes,
            tb_name
        )
    except ValueError as e:
        logger.warning(f"[EXTRACT] Ошибка обработки {url} в 'parse_xls_bytes'")
        return None
    return df


def parse_xls_bytes(file_bytes: bytes, table_name: str) -> pd.DataFrame:
    """
    Синхронный pandas parsing
    """
    file = io.BytesIO(file_bytes)

    df = pd.read_excel(file, header=None, engine="xlrd")

    start_idx = None

    for i, row in df.iterrows():
        if row.astype(str).str.contains(table_name, case=False, na=False).any():
            start_idx = i
            break

    if start_idx is None:
        raise ValueError(f"Таблица '{table_name}' не найдена")

    header_idx = start_idx + 1
    end_idx = None

    for i in range(header_idx + 1, len(df)):
        row = df.iloc[i]

        if row.isna().all():
            end_idx = i
            break

        row_str = row.astype(str)

        if row_str.str.contains("Итого|Всего", case=False, na=False).any():
            end_idx = i
            break

        if row.notna().sum() < 3:
            end_idx = i
            break

    if end_idx is None:
        end_idx = len(df)

    table = df.iloc[header_idx:end_idx].copy()
    table = table.loc[:, table.notna().any()]

    table.columns = table.iloc[0]
    table = table[1:].reset_index(drop=True)

    cols = table.columns
    first_cols = list(cols[:5])
    last_col = [c for c in cols if pd.notna(c)][-1]

    table = table[first_cols + [last_col]]

    table.columns = [
        re.sub(r"\s+", " ", str(col).replace("\n", " ")).strip()
        for col in table.columns
    ]

    table = table.iloc[1:].reset_index(drop=True)

    return table


def extract_target_page_tables(page, tb_name: str) -> List[List[List[str]]]:
    """
    Выделение таблицы с заданным именем с каждой страницы файла
    """
    collecting = False
    collected_tables = []

    tables = page.find_tables()
    logger.info(f"[EXTRACT] Страница {page.page_number}: найдено {len(tables)} таблиц")

    for table in tables:
        top_edge = table.bbox[1]
        header_area = (0, 0, page.width, top_edge)
        header_text = page.within_bbox(header_area).extract_text() or ""

        lines = header_text.strip().split('\n')
        table_name = lines[-1] if lines else ""

        if tb_name in table_name:
            collecting = True

        elif table_name and collecting:
            collecting = False

        if collecting:
            data = table.extract()
            data = [row[:5] + [row[-1]] for row in data]
            collected_tables.append(data)

    return collected_tables


def tables_to_dataframe(tables: List[List[List[str]]]) -> pd.DataFrame:
    """
    Перемещение всех таблиц в структуру pd.DataFrame
    """
    all_rows = []
    header = None

    for table in tables:
        if not table:
            continue

        if header is None:
            if len(table) > 1:
                del table[1]
            else:
                logger.warning("[EXTRACT] Таблица без ожидаемой структуры (нет второй строки в header)")
            header = [col.replace("\n", " ").strip() for col in table[0]]
            rows = table[1:]
        else:
            rows = table

        for row in rows:
            cleaned = [
                (cell.replace("\n", " ").strip() if cell else None)
                for cell in row
            ]
            all_rows.append(cleaned)
    logger.info(f"[EXTRACT] Получено {len(all_rows)} строк таблицы")
    return pd.DataFrame(all_rows, columns=header)

def safe_int(x):
    """Безопасное приведение числовых типов"""
    try:
        if x is None:
            return None
        return int(str(x).replace(" ", "").strip())
    except (ValueError, TypeError):
        return None

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Очистка фрейма данных
    """
    if df.empty:
        return df

    new_df = df.dropna(how="all")
    logger.info("[EXTRACT] Замена '-' на 0 в числовых колонках")
    new_df.iloc[:, 3:] = new_df.iloc[:, 3:].replace('-', '0')
    new_header = [
        "exchange_product_id",
        "exchange_product_name",
        "delivery_basis_name",
        "volume",
        "total",
        "count"
    ]
    new_df.columns = new_header
    new_df["volume"] = new_df["volume"].apply(safe_int)
    new_df["total"] = new_df["total"].apply(safe_int)
    new_df["count"] = new_df["count"].apply(safe_int)
    new_df = new_df[new_df["count"] > 0].reset_index(drop=True)
    logger.info(
        f"[EXTRACT] Очистка данных: {len(df)} -> {len(new_df)} строк "
        f"(удалено {len(df) - len(new_df)})"
    )
    return new_df
