from datetime import datetime

import pandas as pd
import pytest
from sqlalchemy import select, func

from src.load import load_to_db
from src.models import SpimexTradingResults


@pytest.mark.asyncio
async def test_load_to_db_inserts_data(db_session):
    df = pd.DataFrame({
        "exchange_product_id": ["A"],
        "exchange_product_name": ["Oil"],
        "oil_id": ["O1"],
        "delivery_basis_id": ["DB1"],
        "delivery_basis_name": ["Basis"],
        "delivery_type_id": ["D1"],
        "volume": [10],
        "total": [100],
        "count": [1],
        "date": [datetime(2026, 4, 24)],
    })

    await load_to_db(db_session, df)

    result = await db_session.execute(
        select(func.count()).select_from(SpimexTradingResults)
    )
    count = result.scalar()

    assert count == 1
