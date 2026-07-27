from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.core.models.enums import CheckpointStatus, RespondentType


class CheckpointUpdateRequest(BaseModel):
    period_label: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    status: CheckpointStatus | None = None


class ResponsesSummary(BaseModel):
    expected: int
    submitted: int


class CheckpointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    group_id: int
    period_label: str
    period_start: date
    period_end: date
    status: CheckpointStatus
    created_at: datetime
    responses_summary: ResponsesSummary


class CheckpointResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    respondent_type: RespondentType
    respondent_id: int
    attendance_ok: bool | None
    progress_ok: bool | None
    comments: str | None
    submitted_at: datetime | None


class CheckpointPendingRead(BaseModel):
    checkpoint_id: int
    group_id: int
    group_name: str
    period_label: str
    period_end: date
    days_remaining: int
    overdue: bool