from __future__ import annotations

from datetime import date

from fastapi import Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

# TODO: ajustar este import al path real de get_db en tu proyecto
# (el mismo que usa stage_service.py)
from app.core.db.session import get_db

from app.core.repositories import deliverable_repository
from app.core.schemas.deliverable_schema import DeliverableResponse, DeliverableUpdate

VALID_STATUSES = {"Pending", "Submitted", "Late"}


def get_all_deliverables_service(db: Session = Depends(get_db)) -> list[DeliverableResponse]:
    deliverables = deliverable_repository.get_all_deliverables(db)
    return [DeliverableResponse.model_validate(d) for d in deliverables]


def get_deliverable_by_id_service(
    deliverable_id: int, db: Session = Depends(get_db)
) -> DeliverableResponse:
    deliverable = deliverable_repository.get_deliverable_by_id(db, deliverable_id)
    if deliverable is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Deliverable not found"
        )
    return DeliverableResponse.model_validate(deliverable)


def update_deliverable_service(
    deliverable_id: int, data: DeliverableUpdate, db: Session = Depends(get_db)
) -> DeliverableResponse:
    deliverable = deliverable_repository.get_deliverable_by_id(db, deliverable_id)
    if deliverable is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Deliverable not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    updated = deliverable_repository.update_deliverable(db, deliverable, update_data)
    return DeliverableResponse.model_validate(updated)


def get_pending_deliverables_service(db: Session = Depends(get_db)) -> list[DeliverableResponse]:
    deliverables = deliverable_repository.get_deliverables_by_status(db, "Pending")
    return [DeliverableResponse.model_validate(d) for d in deliverables]


def get_overdue_deliverables_service(db: Session = Depends(get_db)) -> list[DeliverableResponse]:
    deliverables = deliverable_repository.get_overdue_deliverables(db, date.today())
    return [DeliverableResponse.model_validate(d) for d in deliverables]