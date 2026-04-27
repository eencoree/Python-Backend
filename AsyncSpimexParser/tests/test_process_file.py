import asyncio

import pytest

from src.main import process_file


class DummySession:
    pass


@pytest.mark.asyncio
async def test_process_file_pdf(monkeypatch):
    import pandas as pd
    from datetime import datetime, date

    async def fake_extract_pdf(*args, **kwargs):
        return pd.DataFrame({
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

    def fake_clean_df(df):
        return df

    def fake_transform_df(df, file_date):
        return df

    monkeypatch.setattr("src.main.extract_pdf", fake_extract_pdf)
    monkeypatch.setattr("src.main.clean_df", fake_clean_df)
    monkeypatch.setattr("src.main.transform_df", fake_transform_df)

    df, url, dt = await process_file(
        "https://spimex.com/file.pdf",
        date(2026, 4, 24),
        DummySession(),
        asyncio.Semaphore(1),
    )

    assert df is not None
    assert len(df) == 1
