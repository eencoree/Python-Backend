import logging
from datetime import date

import pandas as pd

logger = logging.getLogger(__name__)


def transform_df(df: pd.DataFrame, file_date: date) -> pd.DataFrame:
    df = df.copy()
    if 'exchange_product_id' not in df.columns:
        logger.error("[TRANSFORM] Отсутствует колонка 'exchange_product_id'")
        raise ValueError("exchange_product_id column is required")

    column = df['exchange_product_id']
    df['oil_id'] = column.str[:4]
    df['delivery_basis_id'] = column.str[4:7]
    df['delivery_type_id'] = column.str[-1]
    df['date'] = file_date
    logger.info(
        f"[TRANSFORM] Добавлены колонки oil_id, delivery_basis_id, delivery_type_id, date "
    )
    return df
