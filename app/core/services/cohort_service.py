from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models.enums import UserRole
from app.core.models.group import Group
from app.core.models.user import User
from app.core.repositories.cohort_repository import CohortRepository
from app.core.schemas.cohort import (
    CohortGroupRead,
    CohortRead,
    CohortStageRead,
    CohortUpsertRequest,
)


class CohortService:

    def __init__(self, repository: CohortRepository | None = None):
        self.repository = repository or CohortRepository()

    def list_cohorts(self, db: Session, year: int | None = None, semester: int | None = None, status: str | None = None, page: int = 1, page_size: int = 10) -> list[CohortRead]:
        cohorts = self.repository.list(db, year=year, semester=semester, status=status, page=page, page_size=page_size)
        return [self._to_read(db, cohort) for cohort in cohorts]

    def get_cohort(self, db: Session, cohort_id: int) -> CohortRead:
        cohort = self._get_or_404(db, cohort_id)
        return self._to_read(db, cohort)

    def upsert_cohort(self, db: Session, payload: CohortUpsertRequest) -> CohortRead:
        if payload.semester not in (1, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Semester must be 1 or 2",
            )
        
        if payload.id is None:
            cohort = self.repository.create(db, payload)
        else:
            cohort = self._get_or_404(db, payload.id)
            cohort = self.repository.update(db, cohort, payload)

        return self._to_read(db, cohort)

    def list_groups(self, db: Session, cohort_id: int, current_user: User) -> list[CohortGroupRead]:
        self._get_or_404(db, cohort_id)
        groups = self.repository.list_groups(db, cohort_id)
        groups = self._filter_groups_for_user(groups, current_user)
        return [CohortGroupRead.model_validate(group, from_attributes=True) for group in groups]

    def list_stages(self, db: Session, cohort_id: int) -> list[CohortStageRead]:
        self._get_or_404(db, cohort_id)
        stages = self.repository.list_stages(db, cohort_id)
        return [CohortStageRead.model_validate(stage, from_attributes=True) for stage in stages]

    def _filter_groups_for_user(self, groups: list[Group], current_user: User) -> list[Group]:
        """Restringe los grupos visibles segun el rol del usuario autenticado."""
        if current_user.role == UserRole.COORDINATOR:
            return groups

        if current_user.role in (UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR):
            return [
                group for group in groups
                if (group.business_tutor and group.business_tutor.user_id == current_user.id)
                or (group.technical_tutor and group.technical_tutor.user_id == current_user.id)
            ]

        if current_user.role == UserRole.STUDENT:
            return [
                group for group in groups
                if any(student.user_id == current_user.id for student in group.students)
            ]

        return []

    def _get_or_404(self, db: Session, cohort_id: int):
        cohort = self.repository.get_by_id(db, cohort_id)
        if cohort is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohort not found",
            )
        return cohort

    def _to_read(self, db: Session, cohort) -> CohortRead:
        cohort_read = CohortRead.model_validate(cohort, from_attributes=True)
        return cohort_read.model_copy(
            update={"group_count": self.repository.count_groups(db, cohort.id)}
        )
