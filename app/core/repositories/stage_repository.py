from sqlalchemy.orm import Session

from app.core.models.stage import Stage
from app.core.models.deliverable import Deliverable
from app.core.schemas.stage import StageUpsert


class StageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Stage]:
        return self.db.query(Stage).all()

    def get_by_id(self, stage_id: int) -> Stage | None:
        return self.db.query(Stage).filter(Stage.id == stage_id).first()

    def create(self, data: StageUpsert) -> Stage:
        stage = Stage(**data.model_dump(exclude={"id"}))
        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)
        return stage

    def update(self, stage: Stage, data: StageUpsert) -> Stage:
        for field, value in data.model_dump(exclude={"id"}).items():
            setattr(stage, field, value)
        self.db.commit()
        self.db.refresh(stage)
        return stage

    def get_expected_deliverables(self, stage_id: int) -> list[Deliverable]:
        return (
            self.db.query(Deliverable)
            .filter(Deliverable.stage_id == stage_id)
            .all()
        )