from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.repositories.cohort_repository import CohortRepository
from app.core.repositories.group_repository import GroupRepository
from app.core.models.stage import Stage
from app.core.models.student import Student
from app.core.models.tutor import Tutor
from app.core.models.enums import TutorRole
from app.core.schemas.group import GroupUpsert, GroupResponse


class GroupService:

    def __init__(self, repository: GroupRepository | None = None):
        self.cohort_repository = CohortRepository()
        self.repository = repository or GroupRepository()

    def list_groups(self, db: Session) -> list[GroupResponse]:
        groups = self.repository.list(db)
        return [GroupResponse.model_validate(g, from_attributes=True) for g in groups]

    def get_group(self, db: Session, group_id: int) -> GroupResponse:
        group = self._get_or_404(db, group_id)
        return GroupResponse.model_validate(group, from_attributes=True)

    def upsert_group(self, db: Session, payload: GroupUpsert) -> GroupResponse:
        target_id = self._normalize_id(payload.id)
        self._ensure_cohort_exists(db, payload.cohort_id)
        self._ensure_students_exist(db, payload.student_ids)
        self._ensure_optional_fk_exists(db, Stage, payload.current_stage_id, "Stage not found")
        self._ensure_tutor_type(db, payload.business_tutor_id, TutorRole.BUSINESS, "Business tutor not found",)
        self._ensure_tutor_type(db, payload.technical_tutor_id, TutorRole.TECHNICAL, "Technical tutor not found",)
        
        if target_id is None:
            group = self.repository.create(db, payload)
        else:
            group = self._get_or_404(db, target_id)
            group = self.repository.update(db, group, payload)

        return GroupResponse.model_validate(group, from_attributes=True)

    def delete_group(self, db: Session, group_id: int) -> None:
        group = self._get_or_404(db, group_id)
        self.repository.delete(db, group)

    def change_stage(self, db: Session, group_id: int, new_stage_id: int) -> GroupResponse:
        group = self._get_or_404(db, group_id)
        group = self.repository.change_stage(db, group, new_stage_id)
        return GroupResponse.model_validate(group, from_attributes=True)

    def get_group_students(self, db: Session, group_id: int) -> list:
        self._get_or_404(db, group_id)
        return []  # TODO: reemplazar cuando exista el módulo de Estudiantes

    def get_group_meetings(self, db: Session, group_id: int) -> list:
        self._get_or_404(db, group_id)
        return []  # TODO: reemplazar cuando exista el módulo de Reuniones

    def get_group_deliverables(self, db: Session, group_id: int) -> list:
        self._get_or_404(db, group_id)
        return []  # TODO: reemplazar cuando exista el módulo de Entregables

    def _get_or_404(self, db: Session, group_id: int):
        group = self.repository.get_by_id(db, group_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )
        return group

    def _ensure_cohort_exists(self, db: Session, cohort_id: int) -> None:
        if self.cohort_repository.get_by_id(db, cohort_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cohort not found: {cohort_id}",
            )

    def _ensure_optional_fk_exists(self, db: Session, model, value: int | None, detail: str) -> None:
        if value is None:
            return

        if db.get(model, value) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{detail}: {value}",
            )
            
    def _ensure_tutor_type(self, db: Session, tutor_id: int | None, expected_role: TutorRole, detail: str,) -> None:
        if tutor_id is None:
            return

        tutor = db.get(Tutor, tutor_id)

        if tutor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{detail}: {tutor_id}",
            )

        if tutor.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tutor {tutor_id} must be a {expected_role} tutor.",
            )
        
    def _ensure_students_exist(self, db: Session, student_ids: list[int]) -> None:
        if len(student_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group must have at least one student",
            )

        for student_id in student_ids:
            if db.get(Student, student_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student not found: {student_id}",
                )

    @staticmethod
    def _normalize_id(value: int | None) -> int | None:
        if value is None or value <= 0:
            return None
        return value

