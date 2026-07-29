from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models.user import User
from app.core.repositories.meeting_repository import MeetingRepository
from app.core.schemas.meeting import (
    GroupMeetingsTotalHoursRead,
    MeetingRead,
    MeetingUpsertRequest,
)
from app.core.services.access import user_can_access_group, user_can_manage_group


class MeetingService:
    def __init__(self, repository: MeetingRepository | None = None):
        self.repository = repository or MeetingRepository()

    def list_meetings(self, db: Session, current_user: User) -> list[MeetingRead]:
        meetings = self.repository.list(db)
        meetings = [m for m in meetings if user_can_access_group(m.group, current_user)]
        return [MeetingRead.model_validate(meeting, from_attributes=True) for meeting in meetings]

    def get_meeting(self, db: Session, meeting_id: int, current_user: User) -> MeetingRead:
        meeting = self._get_or_404(db, meeting_id)
        self._ensure_read_access(meeting, current_user)
        return MeetingRead.model_validate(meeting, from_attributes=True)

    def upsert_meeting(self, db: Session, payload: MeetingUpsertRequest, current_user: User) -> MeetingRead:
        group = self.repository.get_group(db, payload.group_id)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        self._ensure_write_access(group, current_user)

        if payload.id is None:
            meeting = self.repository.create(db, payload)
        else:
            meeting = self._get_or_404(db, payload.id)
            meeting = self.repository.update(db, meeting, payload)
        return MeetingRead.model_validate(meeting, from_attributes=True)

    def delete_meeting(self, db: Session, meeting_id: int, current_user: User) -> None:
        meeting = self._get_or_404(db, meeting_id)
        self._ensure_write_access(meeting.group, current_user)
        self.repository.delete(db, meeting)

    def get_group_total_hours(self, db: Session, group_id: int, current_user: User) -> GroupMeetingsTotalHoursRead:
        group = self.repository.get_group(db, group_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )
        self._ensure_read_access(group, current_user, is_group=True)

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
        # Group capacity = sum of the max_capacity of its assigned tutors
        # (business + technical). Tutors that are not yet assigned
        # contribute 0.
        capacity = 0
        if getattr(group, "business_tutor", None) is not None:
            capacity += group.business_tutor.max_capacity or 0
        if getattr(group, "technical_tutor", None) is not None:
            capacity += group.technical_tutor.max_capacity or 0
        return capacity

    def _ensure_read_access(self, group_or_meeting, current_user: User, is_group: bool = False) -> None:
        group = group_or_meeting if is_group else group_or_meeting.group
        if not user_can_access_group(group, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this meeting",
            )

    def _ensure_write_access(self, group, current_user: User) -> None:
        if not user_can_manage_group(group, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to manage meetings for this group",
            )

    def _get_or_404(self, db: Session, meeting_id: int):
        meeting = self.repository.get_by_id(db, meeting_id)
        if meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found",
            )
        return meeting