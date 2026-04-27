import logging

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import SpimexTradingResults

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


async def load_to_db(
        session: AsyncSession,
        df: pd.DataFrame,
        batch_size: int = 500
) -> None:
    """
    Асинхронная batch-вставка через SQLAlchemy AsyncSession.
    """

    if df.empty:
        logger.warning("[LOAD] Пустой DataFrame, загрузка в БД пропущена")
        return

    rows = df.to_dict(orient="records")
    try:
        logger.info(f"[LOAD] Вставка {len(rows)} строк в БД батчами по {batch_size}")

        for i in range(0, len(rows), batch_size):
            batch = rows[i: i + batch_size]
            stmt = insert(SpimexTradingResults).values(batch)
            upsert_stmt = stmt.on_conflict_do_nothing(constraint='uniq_product_date')
            await session.execute(upsert_stmt)
        await session.commit()
        logger.info(f"[LOAD] Успешно вставлено {len(df)} строк")

    except Exception as e:
        await session.rollback()
        logger.error("[LOAD] Ошибка при вставке данных", exc_info=e)
        raise
