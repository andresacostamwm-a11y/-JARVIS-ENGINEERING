from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import get_settings
from app.services.ai import get_ai_provider

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    settings = get_settings()
    ai = get_ai_provider()
    return {
        "status": "ok" if db_ok else "degraded",
        "version": settings.app_version,
        "database": db_ok,
        "ai_available": ai.is_available(),
        "ai_provider": ai.name,
    }
