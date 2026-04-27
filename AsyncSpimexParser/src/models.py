from datetime import datetime

from sqlalchemy import func, UniqueConstraint
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class SpimexTradingResults(Base):
    __tablename__ = 'spimex_trading_results'
    __table_args__ = (
        UniqueConstraint("exchange_product_id", "date", name="uniq_product_date"),
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
    date: Mapped[datetime] = mapped_column(nullable=False)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
