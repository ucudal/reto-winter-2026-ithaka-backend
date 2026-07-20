from sqlalchemy.orm import Session

from app.core.models.deliverable import Deliverable
from app.core.models.stage import Stage
from app.core.repositories.stage_repository import StageRepository
from app.core.schemas.stage import StageUpsert


class StageService:
    def __init__(self, db: Session):
        self.repository = StageRepository(db)

    def get_all(self) -> list[Stage]:
        return self.repository.get_all()

    def upsert(self, stage_id: int, data: StageUpsert) -> Stage:
        return self.repository.upsert(stage_id, data)

    def get_expected_deliverables(self, stage_id: int) -> list[Deliverable] | None:
        stage = self.repository.get_by_id(stage_id)
        if stage is None:
            return None
        return self.repository.get_expected_deliverables(stage_id)