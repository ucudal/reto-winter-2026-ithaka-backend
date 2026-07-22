from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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

    def list_cohorts(self, db: Session) -> list[CohortRead]:
        cohorts = self.repository.list(db)
        return [self._to_read(db, cohort) for cohort in cohorts]

    def get_cohort(self, db: Session, cohort_id: int) -> CohortRead:
        cohort = self._get_or_404(db, cohort_id)
        return self._to_read(db, cohort)

    def upsert_cohort(self, db: Session, payload: CohortUpsertRequest) -> CohortRead:
        if payload.id is None:
            cohort = self.repository.create(db, payload)
        else:
            cohort = self._get_or_404(db, payload.id)
            cohort = self.repository.update(db, cohort, payload)

        return self._to_read(db, cohort)

    def list_groups(self, db: Session, cohort_id: int) -> list[CohortGroupRead]:
        self._get_or_404(db, cohort_id)
        groups = self.repository.list_groups(db, cohort_id)
        return [CohortGroupRead.model_validate(group, from_attributes=True) for group in groups]

    def list_stages(self, db: Session, cohort_id: int) -> list[CohortStageRead]:
        self._get_or_404(db, cohort_id)
        stages = self.repository.list_stages(db, cohort_id)
        return [CohortStageRead.model_validate(stage, from_attributes=True) for stage in stages]

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
