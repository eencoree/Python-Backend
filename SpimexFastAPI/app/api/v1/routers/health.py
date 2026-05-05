from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("/")
async def health_check(
        session: Annotated[AsyncSession, Depends(db_helper.get_session)],
):
    try:
        await session.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {"status": "ok", "database_status": db_status}