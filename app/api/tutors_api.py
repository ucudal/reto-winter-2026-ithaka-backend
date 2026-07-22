from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.tutor import TutorCapacityRead, TutorGroupRead, TutorRead, TutorUpdateRequest
from app.core.services.tutor_service import TutorService

router = APIRouter(prefix="/api/tutors", tags=["Tutors"])
service = TutorService()


@router.get("", response_model=list[TutorRead])
def list_tutors(db: Session = Depends(get_db)):
    return service.list_tutors(db)


@router.get("/overloaded", response_model=list[TutorCapacityRead])
def list_overloaded_tutors(db: Session = Depends(get_db)):
    return service.list_overloaded(db)


@router.get("/{id}", response_model=TutorRead)
def get_tutor(id: int, db: Session = Depends(get_db)):
    return service.get_tutor(db, id)


@router.put("/{id}", response_model=TutorRead)
def update_tutor(id: int, payload: TutorUpdateRequest, db: Session = Depends(get_db)):
    return service.update_tutor(db, id, payload)


@router.get("/{id}/groups", response_model=list[TutorGroupRead])
def get_tutor_groups(id: int, db: Session = Depends(get_db)):
    return service.get_tutor_groups(db, id)


@router.get("/{id}/capacity", response_model=TutorCapacityRead)
def get_tutor_capacity(id: int, db: Session = Depends(get_db)):
    return service.get_tutor_capacity(db, id)