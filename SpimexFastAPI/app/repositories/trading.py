from datetime import date

from sqlalchemy import select, distinct, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SpimexTradingResult


class TradingRepository:
    @staticmethod
    def apply_filters(
            stmt: Select,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> Select[SpimexTradingResult]:
        filters = []
        if oil_id:
            filters.append(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id:
            filters.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id:
            filters.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        if filters:
            stmt = stmt.where(*filters)
        return stmt


    async def get_last_trading_dates(
            self,
            last_days: int,
            session: AsyncSession
    ) -> list[SpimexTradingResult]:
        stmt = (
            select(distinct(SpimexTradingResult.date))
            .order_by(SpimexTradingResult.date.desc())
        )
        if last_days:
            stmt = stmt.limit(last_days)
        result = await session.scalars(stmt)
        return list(result)

    async def get_trading_results(
            self,
            session: AsyncSession,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
            limit: int = 100,
    ) -> list[SpimexTradingResult]:
        stmt = select(SpimexTradingResult)
        stmt = self.apply_filters(stmt, oil_id, delivery_type_id, delivery_basis_id)
        stmt = stmt.order_by(SpimexTradingResult.date.desc()).limit(limit)
        result = await session.scalars(stmt)
        return list(result)


    async def get_dynamics(
            self,
            session: AsyncSession,
            start_date: date,
            end_date: date,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> list[SpimexTradingResult]:
        stmt = select(SpimexTradingResult)
        stmt = self.apply_filters(stmt, oil_id, delivery_type_id, delivery_basis_id)
        stmt = stmt.where(SpimexTradingResult.date.between(start_date, end_date))
        stmt = stmt.order_by(SpimexTradingResult.date.desc())
        result = await session.scalars(stmt)
        return list(result)
