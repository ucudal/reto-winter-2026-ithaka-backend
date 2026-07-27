from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.schemas.tutor import TutorCapacityRead, TutorGroupRead, TutorRead, TutorUpsertRequest
from app.core.security import require_roles, require_authenticated, require_coordinator, require_tutor_or_coordinator
from app.core.services.tutor_service import TutorService

router = APIRouter(prefix="/api/tutors", tags=["Tutors"])
service = TutorService()


@router.get("", response_model=list[TutorRead], dependencies=[Depends(require_authenticated)])
def list_tutors(
    db: Session = Depends(get_db)):
    return service.list_tutors(db)


@router.get("/overloaded", response_model=list[TutorCapacityRead], dependencies=[Depends(require_coordinator)],)
def list_overloaded_tutors(
    db: Session = Depends(get_db)):
    return service.list_overloaded(db)


@router.get("/{id}", response_model=TutorRead, dependencies=[Depends(require_authenticated)])
def get_tutor(
    id: int = None,
    db: Session = Depends(get_db)
):
    return service.get_tutor(db, id)


@router.put("", response_model=TutorRead, dependencies=[Depends(require_coordinator)],)
def upsert_tutor(
    payload: TutorUpsertRequest,
    db: Session = Depends(get_db),
):
    return service.upsert_tutor(db, payload)


@router.get("/{id}/groups", response_model=list[TutorGroupRead], dependencies=[Depends(require_tutor_or_coordinator)])
def get_tutor_groups(id: int, db: Session = Depends(get_db)):
    return service.get_tutor_groups(db, id)


@router.get("/{id}/capacity", response_model=TutorCapacityRead, dependencies=[Depends(require_tutor_or_coordinator)])
def get_tutor_capacity(id: int, db: Session = Depends(get_db)):
    return service.get_tutor_capacity(db, id)
