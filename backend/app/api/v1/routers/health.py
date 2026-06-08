from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "up"
    try:
        result = await db.execute(text("SELECT 1"))
        await result.fetchone()
    except Exception:
        db_status = "down"

    return {"status": "ok", "database": db_status}
