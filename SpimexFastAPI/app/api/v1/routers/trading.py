from typing import Annotated

from fastapi import Depends, Request
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_settings
from app.schemas import TradingDatesQuery, TradingDatesResponse, TradingResultResponse, TradingResultsQuery, \
    DynamicsResponse, DynamicsResultsQuery
from app.services import TradingService

router = APIRouter(
    prefix="/v1/trading",
)
settings = get_settings()


def get_trading_service(request: Request) -> TradingService:
    return request.app.state.trading_service


@router.get("/dates", response_model=TradingDatesResponse)
async def get_dates(
        session: Annotated[AsyncSession, Depends(get_db)],
        query: Annotated[TradingDatesQuery, Depends()],
        service: Annotated[TradingService, Depends(get_trading_service)]
):
    dates = await service.get_last_trading_dates(
        session=session,
        last_days=query.last_days
    )

    return TradingDatesResponse(dates=dates)


@router.get("/results", response_model=list[TradingResultResponse])
async def get_results(
        session: Annotated[AsyncSession, Depends(get_db)],
        query: Annotated[TradingResultsQuery, Depends()],
        service: Annotated[TradingService, Depends(get_trading_service)]
):
    data = await service.get_trading_results(
        session=session,
        oil_id=query.oil_id,
        delivery_type_id=query.delivery_type_id,
        delivery_basis_id=query.delivery_basis_id,
        limit=query.limit,
    )

    return data


@router.get("/dynamics", response_model=list[DynamicsResponse])
async def get_dynamics(
        session: Annotated[AsyncSession, Depends(get_db)],
        query: Annotated[DynamicsResultsQuery, Depends()],
        service: Annotated[TradingService, Depends(get_trading_service)]
):
    data = await service.get_dynamics(
        session=session,
        start_date=query.start_date,
        end_date=query.end_date,
        oil_id=query.oil_id,
        delivery_type_id=query.delivery_type_id,
        delivery_basis_id=query.delivery_basis_id,
    )

    return data
