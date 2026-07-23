from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.models.group import Group
from app.core.models.student import Student
from app.core.schemas.group import GroupUpsert


class GroupRepository:

    def list(self, db: Session) -> list[Group]:
        statement = select(Group).order_by(Group.name.asc(), Group.id.asc())
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, group_id: int) -> Group | None:
        return db.get(Group, group_id)

    def create(self, db: Session, payload: GroupUpsert) -> Group:
        group = Group(**payload.model_dump(exclude={"id", "student_ids"}))
        db.add(group)
        db.flush()
        self._sync_students(db, group, payload.student_ids)
        self._sync_id_sequence(db)
        db.commit()
        db.refresh(group)
        return group

    def update(self, db: Session, group: Group, payload: GroupUpsert) -> Group:
        for field, value in payload.model_dump(exclude={"id", "student_ids"}).items():
            setattr(group, field, value)

        self._sync_students(db, group, payload.student_ids)
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

    def _sync_students(self, db: Session, group: Group, student_ids: list[int]) -> None:
        students: list[Student] = []
        for student_id in student_ids:
            student = db.get(Student, student_id)
            if student is None:
                raise ValueError(f"Student not found: {student_id}")
            students.append(student)

        group.students = students
