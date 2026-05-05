from datetime import datetime, date

from sqlalchemy import func, UniqueConstraint, Index, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SpimexTradingResult(Base):
    __tablename__ = 'spimex_trading_results'
    __table_args__ = (
        UniqueConstraint("exchange_product_id", "date", name="uniq_product_date"),
        Index("index_date", "date"),
        Index(
            "index_filters",
            "oil_id",
            "delivery_type_id",
            "delivery_basis_id"
        ),
        Index(
            "index_date_filters",
            "date",
            "oil_id",
        )
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_product_id: Mapped[str] = mapped_column(nullable=False)
    exchange_product_name: Mapped[str] = mapped_column(nullable=False)
    oil_id: Mapped[str] = mapped_column(nullable=False)
    delivery_basis_id: Mapped[str] = mapped_column(nullable=False)
    delivery_basis_name: Mapped[str] = mapped_column(nullable=False)
    delivery_type_id: Mapped[str] = mapped_column(nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)
    total: Mapped[int] = mapped_column(nullable=False)
    count: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
