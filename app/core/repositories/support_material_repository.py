from __future__ import annotations
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.core.models.support_material import SupportMaterial
from app.core.schemas.support_material import SupportMaterialUpsertRequest


class SupportMaterialRepository:
    def list(self, db: Session) -> list[SupportMaterial]:
        statement = select(SupportMaterial).order_by(
            SupportMaterial.stage_id.asc(), SupportMaterial.id.asc()
        )
        return list(db.scalars(statement).all())

    def list_by_stage(self, db: Session, stage_id: int) -> list[SupportMaterial]:
        statement = (
            select(SupportMaterial)
            .where(SupportMaterial.stage_id == stage_id)
            .order_by(SupportMaterial.id.asc())
        )
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, material_id: int) -> SupportMaterial | None:
        return db.get(SupportMaterial, material_id)

    def create(
        self, db: Session, payload: SupportMaterialUpsertRequest
    ) -> SupportMaterial:
        material = SupportMaterial(**payload.model_dump(exclude={"id"}))
        db.add(material)
        db.flush()
        self._sync_id_sequence(db)
        db.commit()
        db.refresh(material)
        return material

    def update(
        self,
        db: Session,
        material: SupportMaterial,
        payload: SupportMaterialUpsertRequest,
    ) -> SupportMaterial:
        for field, value in payload.model_dump(exclude={"id"}).items():
            setattr(material, field, value)
        db.commit()
        db.refresh(material)
        return material

    def delete(self, db: Session, material: SupportMaterial) -> None:
        db.delete(material)
        db.commit()

    def _sync_id_sequence(self, db: Session) -> None:
        sequence_name = db.scalar(
            text("SELECT pg_get_serial_sequence('support_materials', 'id')")
        )
        if sequence_name is None:
            return
        db.execute(
            text(
                "SELECT setval(:sequence_name, "
                "COALESCE((SELECT MAX(id) FROM support_materials), 1), true)"
            ),
            {"sequence_name": sequence_name},
        )