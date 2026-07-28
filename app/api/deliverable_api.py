from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.schemas.deliverable import DeliverableRead, DeliverableUpdate
from app.core.security import require_authenticated, require_tutor_or_coordinator
from app.core.services.deliverable_service import DeliverableService, get_deliverable_service

router = APIRouter(prefix="/api/deliverables", tags=["deliverables"])


# /pending y /overdue van antes de /{deliverable_id} para que no las matchee como id

@router.get("/pending", response_model=list[DeliverableRead], dependencies=[Depends(require_tutor_or_coordinator)])
def get_pending_deliverables(service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_pending()


@router.get("/overdue", response_model=list[DeliverableRead], dependencies=[Depends(require_tutor_or_coordinator)])
def get_overdue_deliverables(service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_overdue()


@router.get("", response_model=list[DeliverableRead], dependencies=[Depends(require_authenticated)])
def list_deliverables(service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_all()


@router.get("/{deliverable_id}", response_model=DeliverableRead, dependencies=[Depends(require_authenticated)])
def get_deliverable(deliverable_id: int, service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_by_id(deliverable_id)


@router.put("", response_model=DeliverableRead, dependencies=[Depends(require_tutor_or_coordinator)])
def update_deliverable(
    data: DeliverableUpdate,
    service: DeliverableService = Depends(get_deliverable_service),
):
    return service.update(data)
