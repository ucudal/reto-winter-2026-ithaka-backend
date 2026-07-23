from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.models.group import Group
from app.core.models.meeting import Meeting
from app.core.schemas.meeting import MeetingUpdateRequest


class MeetingRepository:
    def list(self, db: Session) -> list[Meeting]:
        statement = select(Meeting).order_by(Meeting.date.desc(), Meeting.id.desc())
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, meeting_id: int) -> Meeting | None:
        return db.get(Meeting, meeting_id)

    def update(self, db: Session, meeting: Meeting, payload: MeetingUpdateRequest) -> Meeting:
        for field, value in payload.model_dump().items():
            setattr(meeting, field, value)
        db.commit()
        db.refresh(meeting)
        return meeting

    def delete(self, db: Session, meeting: Meeting) -> None:
        db.delete(meeting)
        db.commit()

    def sum_hours_by_group(self, db: Session, group_id: int) -> float:
        statement = select(func.coalesce(func.sum(Meeting.hours_spent), 0)).where(
            Meeting.group_id == group_id
        )
        return float(db.scalar(statement) or 0)

    def get_group(self, db: Session, group_id: int) -> Group | None:
        return db.get(Group, group_id)
    