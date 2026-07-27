from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models.tutor import Tutor
from app.core.repositories.tutor_repository import TutorRepository
from app.core.schemas.tutor import TutorRead, TutorUpsertRequest


class TutorService:

    def __init__(self):
        self.repo = TutorRepository()

    def list_tutors(self, db: Session) -> list[Tutor]:
        return self.repo.list(db)

    def get_tutor(self, db: Session, tutor_id: int) -> Tutor:
        tutor = self.repo.get_by_id(db, tutor_id)
        if tutor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tutor {tutor_id} not found")
        return tutor

    def upsert_tutor(self, db: Session, payload: TutorUpsertRequest) -> TutorRead:
        if payload.id is None:
            tutor = self.repo.create(db, payload)
        else:
            tutor = self.repo.get_by_id(db, payload.id)

        if tutor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found",
            )

        tutor = self.repo.update(db, tutor, payload)

        return TutorRead.model_validate(tutor)

    def get_tutor_groups(self, db: Session, tutor_id: int):
        self.get_tutor(db, tutor_id)  # valida que exista, o lanza 404
        return self.repo.list_groups(db, tutor_id)

    def get_tutor_capacity(self, db: Session, tutor_id: int) -> dict:
        tutor = self.get_tutor(db, tutor_id)
        meetings = self.repo.list_meetings(db, tutor_id)
        return self._build_capacity(tutor, meetings)

    def list_overloaded(self, db: Session) -> list[dict]:
        tutors = self.repo.list(db)
        result = []
        for tutor in tutors:
            meetings = self.repo.list_meetings(db, tutor.id)
            capacity = self._build_capacity(tutor, meetings)
            if capacity["overloaded"]:
                result.append(capacity)
        return result

    def _build_capacity(self, tutor: Tutor, meetings: list) -> dict:
        assigned_hours = sum(float(m.hours_spent or 0) for m in meetings)
        available_hours = max(tutor.max_capacity - assigned_hours, 0)
        usage_percentage = (
            round((assigned_hours / tutor.max_capacity) * 100, 1) if tutor.max_capacity else 0
        )
        return {
            "tutor_id": tutor.id,
            "max_capacity": tutor.max_capacity,
            "assigned_hours": assigned_hours,
            "available_hours": available_hours,
            "usage_percentage": usage_percentage,
            "overloaded": assigned_hours > tutor.max_capacity,
        }
