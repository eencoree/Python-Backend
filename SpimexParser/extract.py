import io
import logging
import re
import urllib
from contextlib import contextmanager
from datetime import time
from typing import List

import pandas as pd
import pdfplumber
import requests

logger = logging.getLogger(__name__)


@contextmanager
def pdf_generator(url: str, retries: int = 3):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(retries):
        try:
            logger.info(f"[EXTRACT] Скачивание PDF: {url} (попытка {attempt + 1})")

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                pdf_bytes = response.read()

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                yield pdf.pages
                return

        except Exception as e:
            logger.warning(f"[EXTRACT] Ошибка скачивания (попытка {attempt + 1}): {e}")
            time.sleep(2)

    logger.error(f"[EXTRACT] Не удалось скачать PDF после {retries} попыток: {url}")
    raise Exception(f"Download failed: {url}")


def extract_xls(url: str, table_name: str, session: requests.Session | None = None) -> pd.DataFrame:
    headers = {"User-Agent": "Mozilla/5.0"}

    requester = session if session else requests

    response = requester.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    file = io.BytesIO(response.content)

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

    logger.info(f"[EXTRACT] Страница {page.page_number}: найдено {len(collected_tables)} таблиц '{tb_name}'")
    return collected_tables


def tables_to_dataframe(tables: List[List[List[str]]]) -> pd.DataFrame:
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


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
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
    new_df["volume"] = new_df["volume"].astype(int)
    new_df["total"] = new_df["total"].astype(int)
    new_df["count"] = new_df["count"].astype(int)
    new_df = new_df[new_df["count"] > 0].reset_index(drop=True)
    logger.info(
        f"[EXTRACT] Очистка данных: {len(df)} -> {len(new_df)} строк "
        f"(удалено {len(df) - len(new_df)})"
    )
    return new_df
