from __future__ import annotations
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.repositories.support_material_repository import (
    SupportMaterialRepository,
)
from app.core.schemas.support_material import (
    SupportMaterialRead,
    SupportMaterialUpsertRequest,
)


class SupportMaterialService:
    def __init__(self, repository: SupportMaterialRepository | None = None):
        self.repository = repository or SupportMaterialRepository()

    def list_materials(self, db: Session) -> list[SupportMaterialRead]:
        materials = self.repository.list(db)
        return [self._to_read(material) for material in materials]

    def list_by_stage(
        self, db: Session, stage_id: int
    ) -> list[SupportMaterialRead]:
        materials = self.repository.list_by_stage(db, stage_id)
        return [self._to_read(material) for material in materials]

    def upsert_material(
        self, db: Session, payload: SupportMaterialUpsertRequest
    ) -> SupportMaterialRead:
        if payload.id is None:
            material = self.repository.create(db, payload)
        else:
            existing = self._get_or_404(db, payload.id)
            material = self.repository.update(db, existing, payload)
        return self._to_read(material)

    def delete_material(self, db: Session, material_id: int) -> None:
        material = self._get_or_404(db, material_id)
        self.repository.delete(db, material)

    def _get_or_404(self, db: Session, material_id: int):
        material = self.repository.get_by_id(db, material_id)
        if material is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support material not found",
            )
        return material

    def _to_read(self, material) -> SupportMaterialRead:
        return SupportMaterialRead.model_validate(material, from_attributes=True)