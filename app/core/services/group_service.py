from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.repositories.group_repository import GroupRepository
from app.core.schemas.group import GroupCreate, GroupUpdate, GroupResponse


class GroupService:

    def __init__(self, repository: GroupRepository | None = None):
        self.repository = repository or GroupRepository()

    def list_groups(self, db: Session) -> list[GroupResponse]:
        groups = self.repository.list(db)
        return [GroupResponse.model_validate(g, from_attributes=True) for g in groups]

    def get_group(self, db: Session, group_id: int) -> GroupResponse:
        group = self._get_or_404(db, group_id)
        return GroupResponse.model_validate(group, from_attributes=True)

    def create_group(self, db: Session, payload: GroupCreate) -> GroupResponse:
        group = self.repository.create(db, payload)
        return GroupResponse.model_validate(group, from_attributes=True)

    def update_group(self, db: Session, group_id: int, payload: GroupUpdate) -> GroupResponse:
        group = self._get_or_404(db, group_id)
        group = self.repository.update(db, group, payload)
        return GroupResponse.model_validate(group, from_attributes=True)

    def delete_group(self, db: Session, group_id: int) -> None:
        group = self._get_or_404(db, group_id)
        self.repository.delete(db, group)

    def change_stage(self, db: Session, group_id: int, new_stage_id: int) -> GroupResponse:
        group = self._get_or_404(db, group_id)
        group = self.repository.change_stage(db, group, new_stage_id)
        return GroupResponse.model_validate(group, from_attributes=True)

    def get_group_students(self, db: Session, group_id: int) -> list:
        self._get_or_404(db, group_id)
        return []  # TODO: reemplazar cuando exista el módulo de Estudiantes

    def get_group_meetings(self, db: Session, group_id: int) -> list:
        self._get_or_404(db, group_id)
        return []  # TODO: reemplazar cuando exista el módulo de Reuniones

    def get_group_deliverables(self, db: Session, group_id: int) -> list:
        self._get_or_404(db, group_id)
        return []  # TODO: reemplazar cuando exista el módulo de Entregables

    def _get_or_404(self, db: Session, group_id: int):
        group = self.repository.get_by_id(db, group_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )
        return group