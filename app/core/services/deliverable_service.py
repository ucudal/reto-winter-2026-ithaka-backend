from __future__ import annotations

from datetime import date

from fastapi import Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

# TODO: importar get_db del mismo lugar de donde lo importa stage_service.py
from app.core.db.session import get_db

from app.core.repositories import deliverable_repository
from app.core.schemas.deliverable_scheme import DeliverableRead, DeliverableUpdate

VALID_STATUSES = {"Pending", "Submitted", "Late"}


class DeliverableService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[DeliverableRead]:
        deliverables = deliverable_repository.get_all_deliverables(self.db)
        return [DeliverableRead.model_validate(d) for d in deliverables]

    def get_by_id(self, deliverable_id: int) -> DeliverableRead:
        deliverable = deliverable_repository.get_deliverable_by_id(self.db, deliverable_id)
        if deliverable is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail="Deliverable not found"
            )
        return DeliverableRead.model_validate(deliverable)

    def update(self, deliverable_id: int, data: DeliverableUpdate) -> DeliverableRead:
        deliverable = deliverable_repository.get_deliverable_by_id(self.db, deliverable_id)
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

        updated = deliverable_repository.update_deliverable(self.db, deliverable, update_data)
        return DeliverableRead.model_validate(updated)

    def get_pending(self) -> list[DeliverableRead]:
        deliverables = deliverable_repository.get_deliverables_by_status(self.db, "Pending")
        return [DeliverableRead.model_validate(d) for d in deliverables]

    def get_overdue(self) -> list[DeliverableRead]:
        deliverables = deliverable_repository.get_overdue_deliverables(self.db, date.today())
        return [DeliverableRead.model_validate(d) for d in deliverables]


def get_deliverable_service(db: Session = Depends(get_db)) -> DeliverableService:
    return DeliverableService(db)