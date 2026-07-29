from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.enums import TutorRole
from app.core.schemas.tutor import TutorCapacityRead, TutorGroupRead, TutorRead, TutorUpsertRequest
from app.core.services.tutor_service import TutorService

router = APIRouter(prefix="/api/tutors", tags=["Tutors"])

def get_tutor_service() -> TutorService:
    return TutorService()


@router.get("", response_model=list[TutorRead])
def list_tutors(
    role: TutorRole | None = Query(None),
    status: str | None = Query(None),
    search: str |None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    service: TutorService = Depends(get_tutor_service),
):
    return service.list_tutors(
        db,
        role=role,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get("/overloaded", response_model=list[TutorCapacityRead])
def list_overloaded_tutors(db: Session = Depends(get_db), service: TutorService = Depends(get_tutor_service),):
    return service.list_overloaded(db)


@router.get("/{id}", response_model=TutorRead)
def get_tutor(id: int, db: Session = Depends(get_db), service: TutorService = Depends(get_tutor_service),):
    return service.get_tutor(db, id)


@router.put("", response_model=TutorRead)
def upsert_tutor(
    payload: TutorUpsertRequest,
    db: Session = Depends(get_db),
    service: TutorService = Depends(get_tutor_service),
):
    return service.upsert_tutor(db, payload)


@router.get("/{id}/groups", response_model=list[TutorGroupRead])
def get_tutor_groups(id: int, db: Session = Depends(get_db), service: TutorService = Depends(get_tutor_service),):
    return service.get_tutor_groups(db, id)


@router.get("/{id}/capacity", response_model=TutorCapacityRead)
def get_tutor_capacity(id: int, db: Session = Depends(get_db), service: TutorService = Depends(get_tutor_service),):
    return service.get_tutor_capacity(db, id)
