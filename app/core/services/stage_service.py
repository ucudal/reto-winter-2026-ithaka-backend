from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.deliverable import Deliverable
from app.core.models.stage import Stage
from app.core.repositories.cohort_repository import CohortRepository
from app.core.repositories.stage_repository import StageRepository
from app.core.schemas.stage import StageUpsert


class StageService:
    def __init__(self, db: Session):
        self.cohort_repository = CohortRepository()
        self.repository = StageRepository(db)

    def get_all(self) -> list[Stage]:
        return self.repository.get_all()

    def upsert(self, data: StageUpsert) -> Stage:
        stage_id = self._normalize_id(data.id)
        self._ensure_cohort_exists(data.cohort_id)

        if stage_id is None:
            return self.repository.create(data)

        stage = self.repository.get_by_id(stage_id)
        if stage is None:
            raise HTTPException(status_code=404, detail="Etapa no encontrada.")

        return self.repository.update(stage, data)

    def get_expected_deliverables(self, stage_id: int) -> list[Deliverable] | None:
        stage = self.repository.get_by_id(stage_id)
        if stage is None:
            raise HTTPException (status_code=404,detail="Etapa invalida.") 
        return self.repository.get_expected_deliverables(stage_id)

    @staticmethod
    def _normalize_id(value: int | None) -> int | None:
        if value is None or value <= 0:
            return None
        return value

    def _ensure_cohort_exists(self, cohort_id: int) -> None:
        if self.cohort_repository.get_by_id(self.repository.db, cohort_id) is None:
            raise HTTPException(status_code=404, detail="Cohort not found.")


def get_stage_service(db: Session = Depends(get_db)) -> StageService:
    return StageService(db)