from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.support_material import (
    SupportMaterialRead,
    SupportMaterialUpsertRequest,
)
from app.core.services.support_material_service import SupportMaterialService

router = APIRouter(
    prefix="/api/materials",
    tags=["Support Materials"],
)


def get_support_material_service() -> SupportMaterialService:
    return SupportMaterialService()


@router.get("", response_model=list[SupportMaterialRead])
def list_materials(
    stage_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    return service.list_materials(db, stage_id=stage_id, search=search, page=page, page_size=page_size
    )



@router.get("/stage/{stage_id}", response_model=list[SupportMaterialRead])
def list_materials_by_stage(
    stage_id: int,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    return service.list_by_stage(db, stage_id)


@router.post("", response_model=SupportMaterialRead, status_code=201)
def create_material(
    payload: SupportMaterialUpsertRequest,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    return service.upsert_material(db, payload)


@router.put("/{material_id}", response_model=SupportMaterialRead)
def update_material(
    material_id: int,
    payload: SupportMaterialUpsertRequest,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    payload = payload.model_copy(update={"id": material_id})
    return service.upsert_material(db, payload)


@router.delete("/{material_id}", status_code=204)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    service.delete_material(db, material_id)