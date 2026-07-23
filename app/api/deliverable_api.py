from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.schemas.deliverable_schema import DeliverableResponse, DeliverableUpdate
from app.core.services import deliverable_service

router = APIRouter(prefix="/api/deliverables", tags=["Deliverables"])

@router.get("/pending", response_model=list[DeliverableResponse])
def get_pending_deliverables(
    deliverables: list[DeliverableResponse] = Depends(deliverable_service.get_pending_deliverables_service),
):
    return deliverables


@router.get("/overdue", response_model=list[DeliverableResponse])
def get_overdue_deliverables(
    deliverables: list[DeliverableResponse] = Depends(deliverable_service.get_overdue_deliverables_service),
):
    return deliverables


@router.get("", response_model=list[DeliverableResponse])
def get_deliverables(
    deliverables: list[DeliverableResponse] = Depends(deliverable_service.get_all_deliverables_service),
):
    return deliverables


@router.get("/{deliverable_id}", response_model=DeliverableResponse)
def get_deliverable(
    deliverable: DeliverableResponse = Depends(deliverable_service.get_deliverable_by_id_service),
):
    return deliverable


@router.put("/{deliverable_id}", response_model=DeliverableResponse)
def update_deliverable(
    deliverable: DeliverableResponse = Depends(deliverable_service.update_deliverable_service),
):
    return deliverable