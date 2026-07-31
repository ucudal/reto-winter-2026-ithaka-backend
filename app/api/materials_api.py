from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.support_material import (
    SupportMaterialRead,
    SupportMaterialUpsertRequest,
)
from app.core.services.support_material_service import SupportMaterialService
from app.core.security import require_authenticated, require_tutor_or_coordinator, require_coordinator

router = APIRouter(
    prefix="/api/materials",
    tags=["Support Materials"],
)


def get_support_material_service() -> SupportMaterialService:
    return SupportMaterialService()


from app.core.schemas.pagination import PaginatedResponse


@router.get("", response_model=PaginatedResponse[SupportMaterialRead], dependencies=[Depends(require_authenticated)])
def list_materials(
    stage_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    items, total = service.list_materials(
        db, stage_id=stage_id, search=search, page=page, page_size=page_size
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{material_id}", response_model=SupportMaterialRead, dependencies=[Depends(require_authenticated)])
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    return service.get_material(db, material_id)


@router.put("", response_model=SupportMaterialRead, dependencies=[Depends(require_tutor_or_coordinator)])
def upsert_material(
    payload: SupportMaterialUpsertRequest,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    return service.upsert_material(db, payload)


@router.delete("/{material_id}", status_code=204, dependencies=[Depends(require_tutor_or_coordinator)])
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    service: SupportMaterialService = Depends(get_support_material_service),
):
    service.delete_material(db, material_id)