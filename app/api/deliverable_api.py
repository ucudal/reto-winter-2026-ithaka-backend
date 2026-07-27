from __future__ import annotations
 
from fastapi import APIRouter, Depends
 
from app.core.schemas.deliverable_scheme import DeliverableRead, DeliverableUpdate
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
def list_deliverables(service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_all()
 
 
@router.get("/{deliverable_id}", response_model=DeliverableRead)
def get_deliverable(deliverable_id: int, service: DeliverableService = Depends(get_deliverable_service)):
    return service.get_by_id(deliverable_id)
 
 
@router.put("/{deliverable_id}", response_model=DeliverableRead)
def update_deliverable(
    deliverable_id: int,
    data: DeliverableUpdate,
    service: DeliverableService = Depends(get_deliverable_service),
):
    return service.update(deliverable_id, data)