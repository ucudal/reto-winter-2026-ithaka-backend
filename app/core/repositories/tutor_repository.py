from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.enums import TutorRole
from app.core.models.tutor import Tutor
from app.core.models.group import Group
from app.core.models.meeting import Meeting
from app.core.schemas.tutor import TutorUpsertRequest


class TutorRepository:

    def list(
        self,
        db: Session,
        role: TutorRole | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[Tutor]:
        statement = select(Tutor)

        if role is not None:
            statement = statement.where(Tutor.role == role)
        if status is not None:
            statement = statement.where(Tutor.status == status)
        if search:
            statement = statement.where(Tutor.name.ilike(f"%{search}%"))

        statement = statement.order_by(Tutor.name.asc())

        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        return list(db.scalars(statement).all())

    def list_all(self, db: Session) -> list[Tutor]:
        """Trae todos los tutores sin paginar. Uso interno (p. ej. list_overloaded)."""
        statement = select(Tutor).order_by(Tutor.name.asc())
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, tutor_id: int) -> Tutor | None:
        return db.get(Tutor, tutor_id)

    def create(self, db: Session, payload: TutorUpsertRequest) -> Tutor:
        tutor = Tutor(**payload.model_dump(exclude={"id"}))

        db.add(tutor)
        db.commit()
        db.refresh(tutor)
        return tutor

    def update(self, db: Session, tutor: Tutor, payload: TutorUpsertRequest) -> Tutor:
        for field, value in payload.model_dump(exclude={"id"}).items():
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
