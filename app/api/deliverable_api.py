from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.schemas.deliverable import DeliverableRead, DeliverableUpdate
from app.core.services.deliverable_service import DeliverableService, get_deliverable_service

router = APIRouter(prefix="/api/deliverables", tags=["deliverables"])


# /pending y /overdue van antes de /{deliverable_id} para que no las matchee como id

@router.get("/pending", response_model=list[DeliverableRead])
def get_pending_deliverables(service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_pending()


@router.get("/overdue", response_model=list[DeliverableRead])
def get_overdue_deliverables(service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_overdue()


@router.get("", response_model=list[DeliverableRead])
def list_deliverables(
    group_id: int | None = Query(None),
    stage_id: int | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: DeliverableService = Depends(get_deliverable_service),
):
    return service.get_all(
        group_id=group_id, stage_id=stage_id, status=status, page=page, page_size=page_size
    )


@router.get("/{deliverable_id}", response_model=DeliverableRead)
def get_deliverable(deliverable_id: int, service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_by_id(deliverable_id)


@router.put("", response_model=DeliverableRead)
def update_deliverable(
    data: DeliverableUpdate,
    service: DeliverableService = Depends(get_deliverable_service),
):
    return service.update(data)
