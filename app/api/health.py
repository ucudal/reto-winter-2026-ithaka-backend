from fastapi import APIRouter
from sqlalchemy import text

from app.core.db.session import SessionLocal

router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@router.get("/health/db")
def health_check_db():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "reachable"
    }
