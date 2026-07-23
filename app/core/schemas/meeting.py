from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingLink(BaseModel):
    type: str
    url: str


class MeetingBase(BaseModel):
    group_id: int
    tutor_ids: list[int]
    date: datetime
    participants: list[int] | None = None
    notes: str | None = None
    next_steps: str | None = None
    hours_spent: float | None = None
    links: list[MeetingLink] | None = None


class MeetingUpdateRequest(MeetingBase):
    pass


class MeetingRead(MeetingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class GroupMeetingsTotalHoursRead(BaseModel):
    group_id: int
    total_hours: float
    max_capacity: float
    remaining_hours: float
