from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.repositories.meeting_repository import MeetingRepository
from app.core.schemas.meeting import (
    GroupMeetingsTotalHoursRead,
    MeetingRead,
    MeetingUpdateRequest,
)


class MeetingService:
    def __init__(self, repository: MeetingRepository | None = None):
        self.repository = repository or MeetingRepository()

    def list_meetings(self, db: Session) -> list[MeetingRead]:
        meetings = self.repository.list(db)
        return [MeetingRead.model_validate(meeting, from_attributes=True) for meeting in meetings]

    def get_meeting(self, db: Session, meeting_id: int) -> MeetingRead:
        meeting = self._get_or_404(db, meeting_id)
        return MeetingRead.model_validate(meeting, from_attributes=True)

    def update_meeting(
        self, db: Session, meeting_id: int, payload: MeetingUpdateRequest
    ) -> MeetingRead:
        meeting = self._get_or_404(db, meeting_id)
        meeting = self.repository.update(db, meeting, payload)
        return MeetingRead.model_validate(meeting, from_attributes=True)

    def delete_meeting(self, db: Session, meeting_id: int) -> None:
        meeting = self._get_or_404(db, meeting_id)
        self.repository.delete(db, meeting)

    def get_group_total_hours(self, db: Session, group_id: int) -> GroupMeetingsTotalHoursRead:
        group = self.repository.get_group(db, group_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )

        total_hours = self.repository.sum_hours_by_group(db, group_id)
        max_capacity = self._resolve_group_capacity(group)
        remaining_hours = max_capacity - total_hours

        return GroupMeetingsTotalHoursRead(
            group_id=group_id,
            total_hours=total_hours,
            max_capacity=max_capacity,
            remaining_hours=remaining_hours,
        )

    def _resolve_group_capacity(self, group) -> float:
        capacity = 0
        if getattr(group, "business_tutor", None) is not None:
            capacity += group.business_tutor.max_capacity or 0
        if getattr(group, "technical_tutor", None) is not None:
            capacity += group.technical_tutor.max_capacity or 0
        return capacity

    def _get_or_404(self, db: Session, meeting_id: int):
        meeting = self.repository.get_by_id(db, meeting_id)
        if meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found",
            )
        return meeting
    