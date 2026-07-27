from __future__ import annotations
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.models.enums import RespondentType, UserRole
from app.core.models.user import User
from app.core.repositories.checkpoint_repository import CheckpointRepository
from app.core.schemas.checkpoint import (
    CheckpointPendingRead,
    CheckpointRead,
    CheckpointResponseRead,
    CheckpointUpdateRequest,
    ResponsesSummary,
)


class CheckpointService:

    def __init__(self, repository: CheckpointRepository | None = None):
        self.repository = repository or CheckpointRepository()

    def list_checkpoints(self, db: Session, group_id: int | None = None, status_filter: str | None = None) -> list[CheckpointRead]:
        checkpoints = self.repository.list(db, group_id=group_id, status=status_filter)
        return [self._to_read(db, c) for c in checkpoints]

    def get_checkpoint(self, db: Session, checkpoint_id: int) -> CheckpointRead:
        checkpoint = self._get_or_404(db, checkpoint_id)
        return self._to_read(db, checkpoint)

    def update_checkpoint(self, db: Session, checkpoint_id: int, payload: CheckpointUpdateRequest) -> CheckpointRead | None:
        checkpoint = self._get_or_404(db, checkpoint_id)

        if payload.model_dump(exclude_none=True) == {}:
            self.repository.delete(db, checkpoint)
            return None

        checkpoint = self.repository.update(db, checkpoint, payload)
        return self._to_read(db, checkpoint)

    def list_responses(self, db: Session, checkpoint_id: int) -> list[CheckpointResponseRead]:
        self._get_or_404(db, checkpoint_id)
        responses = self.repository.list_responses(db, checkpoint_id)
        return [CheckpointResponseRead.model_validate(r) for r in responses]

    def list_my_pending(self, db: Session, current_user: User) -> list[CheckpointPendingRead]:
        respondent_type, respondent_id, group_ids = self._resolve_respondent(current_user)
        checkpoints = self.repository.list_open_for_group_ids(db, group_ids)

        pending = []
        today = date.today()
        for checkpoint in checkpoints:
            response = self.repository.get_response(db, checkpoint.id, respondent_type, respondent_id)
            if response is not None and response.submitted_at is not None:
                continue

            days_remaining = (checkpoint.period_end - today).days
            pending.append(
                CheckpointPendingRead(
                    checkpoint_id=checkpoint.id,
                    group_id=checkpoint.group_id,
                    group_name=checkpoint.group.name,
                    period_label=checkpoint.period_label,
                    period_end=checkpoint.period_end,
                    days_remaining=days_remaining,
                    overdue=days_remaining < 0,
                )
            )
        return pending

    def _resolve_respondent(self, current_user: User) -> tuple[RespondentType, int, list[int]]:
        if current_user.role == UserRole.STUDENT:
            student = current_user.student
            if student is None or student.group_id is None:
                return RespondentType.STUDENT, 0, []
            return RespondentType.STUDENT, student.id, [student.group_id]

        if current_user.role in (UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR):
            tutor = current_user.tutor
            if tutor is None:
                return RespondentType.TUTOR, 0, []
            group_ids = [g.id for g in tutor.groups_as_business_tutor]
            group_ids += [g.id for g in tutor.groups_as_technical_tutor]
            return RespondentType.TUTOR, tutor.id, group_ids

        return RespondentType.TUTOR, 0, []

    def _to_read(self, db: Session, checkpoint) -> CheckpointRead:
        expected = self.repository.count_expected_responses(db, checkpoint.id)
        submitted = sum(1 for r in checkpoint.responses if r.submitted_at is not None)
        return CheckpointRead.model_validate(checkpoint).model_copy(
            update={"responses_summary": ResponsesSummary(expected=expected, submitted=submitted)}
        )

    def _get_or_404(self, db: Session, checkpoint_id: int):
        checkpoint = self.repository.get_by_id(db, checkpoint_id)
        if checkpoint is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkpoint not found")
        return checkpoint