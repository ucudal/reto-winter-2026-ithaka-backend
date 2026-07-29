from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.models.meeting import MeetingStatus


class MeetingLink(BaseModel):
    type: str
    url: str


class MeetingParticipant(BaseModel):
    student_id: int
    attended: bool = False


class MeetingBase(BaseModel):
    group_id: int
    tutor_ids: list[int] | None = None
    status: MeetingStatus = MeetingStatus.SCHEDULED
    date: datetime
    participants: list[MeetingParticipant] | None = None
    summary: str | None = None
    notes: str | None = None
    next_steps: str | None = None
    hours_spent: float | None = None
    links: list[MeetingLink] | None = None


class MeetingUpsertRequest(MeetingBase):
    id: int | None = None


class MeetingRead(MeetingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class GroupMeetingsTotalHoursRead(BaseModel):
    group_id: int
    total_hours: float
    max_capacity: float
    remaining_hours: float