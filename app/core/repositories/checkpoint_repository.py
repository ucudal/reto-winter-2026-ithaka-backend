from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.models.checkpoint import Checkpoint
from app.core.models.checkpoint_response import CheckpointResponse
from app.core.models.enums import CheckpointStatus, RespondentType
from app.core.models.group import Group


class CheckpointRepository:

    def list(self, db: Session, group_id: int | None = None, status: str | None = None) -> list[Checkpoint]:
        statement = select(Checkpoint)
        if group_id is not None:
            statement = statement.where(Checkpoint.group_id == group_id)
        if status is not None:
            statement = statement.where(Checkpoint.status == status)
        statement = statement.order_by(Checkpoint.period_end.desc())
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, checkpoint_id: int) -> Checkpoint | None:
        return db.get(Checkpoint, checkpoint_id)

    def update(self, db: Session, checkpoint: Checkpoint, payload) -> Checkpoint:
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(checkpoint, field, value)
        db.commit()
        db.refresh(checkpoint)
        return checkpoint

    def delete(self, db: Session, checkpoint: Checkpoint) -> None:
        db.delete(checkpoint)
        db.commit()

    def list_responses(self, db: Session, checkpoint_id: int) -> list[CheckpointResponse]:
        statement = select(CheckpointResponse).where(
            CheckpointResponse.checkpoint_id == checkpoint_id
        )
        return list(db.scalars(statement).all())

    def count_expected_responses(self, db: Session, checkpoint_id: int) -> int:
        checkpoint = db.get(Checkpoint, checkpoint_id)
        group = db.get(Group, checkpoint.group_id)
        expected = len(group.students)
        expected += 1 if group.business_tutor_id else 0
        expected += 1 if group.technical_tutor_id else 0
        return expected

    def list_open_for_group_ids(self, db: Session, group_ids: list[int]) -> list[Checkpoint]:
        if not group_ids:
            return []
        statement = select(Checkpoint).where(
            Checkpoint.group_id.in_(group_ids),
            Checkpoint.status == CheckpointStatus.OPEN,
        )
        return list(db.scalars(statement).all())

    def get_response(
        self, db: Session, checkpoint_id: int, respondent_type: RespondentType, respondent_id: int
    ) -> CheckpointResponse | None:
        statement = select(CheckpointResponse).where(
            CheckpointResponse.checkpoint_id == checkpoint_id,
            CheckpointResponse.respondent_type == respondent_type,
            CheckpointResponse.respondent_id == respondent_id,
        )
        return db.scalars(statement).first()