import logging

import pandas as pd
from sqlalchemy.orm import Session

from models import SpimexTradingResults

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def load_to_db(session: Session, df: pd.DataFrame, batch_size: int = 500):
    if df.empty:
        logger.warning("[LOAD] Пустой DataFrame, загрузка в БД пропущена")
        return

    engine = session.get_bind()
    try:
        logger.info(f"[LOAD_FAST] Вставка {len(df)} строк в БД через pandas.to_sql батчами {batch_size}")

        df.to_sql(
            SpimexTradingResults.__tablename__,
            con=engine,
            index=False,
            if_exists='append',
            method='multi',
            chunksize=batch_size
        )

        logger.info(f"[LOAD_FAST] Успешно вставлено {len(df)} строк")
    except Exception as e:
        session.rollback()
        logger.error("[LOAD_FAST] Ошибка при вставке данных через pandas.to_sql", exc_info=e)
        raise
