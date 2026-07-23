from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.tutor import Tutor
from app.core.models.group import Group
from app.core.models.meeting import Meeting


class TutorRepository:

    def list(self, db: Session) -> list[Tutor]:
        statement = select(Tutor).order_by(Tutor.name.asc())
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, tutor_id: int) -> Tutor | None:
        return db.get(Tutor, tutor_id)

    def update(self, db: Session, tutor: Tutor, **fields) -> Tutor:
        for field, value in fields.items():
            setattr(tutor, field, value)
        db.commit()
        db.refresh(tutor)
        return tutor

    def list_groups(self, db: Session, tutor_id: int) -> list[Group]:
        statement = select(Group).where(
            (Group.business_tutor_id == tutor_id) | (Group.technical_tutor_id == tutor_id)
        )
        return list(db.scalars(statement).all())

    def list_meetings(self, db: Session, tutor_id: int) -> list[Meeting]:
        statement = select(Meeting).where(Meeting.tutor_ids.contains([tutor_id]))
        return list(db.scalars(statement).all())