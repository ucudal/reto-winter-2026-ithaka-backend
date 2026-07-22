from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.models.group import Group
from app.core.schemas.group import GroupCreate, GroupUpdate


class GroupRepository:

    def list(self, db: Session) -> list[Group]:
        statement = select(Group).order_by(Group.name.asc(), Group.id.asc())
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, group_id: int) -> Group | None:
        return db.get(Group, group_id)

    def create(self, db: Session, payload: GroupCreate) -> Group:
        group = Group(**payload.model_dump())
        db.add(group)
        db.flush()
        self._sync_id_sequence(db)
        db.commit()
        db.refresh(group)
        return group

    def update(self, db: Session, group: Group, payload: GroupUpdate) -> Group:
        for field, value in payload.model_dump().items():
            setattr(group, field, value)

        db.commit()
        db.refresh(group)
        return group

    def delete(self, db: Session, group: Group) -> None:
        db.delete(group)
        db.commit()

    def change_stage(self, db: Session, group: Group, new_stage_id: int) -> Group:
        group.current_stage_id = new_stage_id
        db.commit()
        db.refresh(group)
        return group

    def _sync_id_sequence(self, db: Session) -> None:
        sequence_name = db.scalar(text("SELECT pg_get_serial_sequence('groups', 'id')"))
        if sequence_name is None:
            return

        db.execute(
            text("SELECT setval(:sequence_name, COALESCE((SELECT MAX(id) FROM groups), 1), true)"),
            {"sequence_name": sequence_name},
        )