from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }
