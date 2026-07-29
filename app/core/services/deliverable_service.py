from __future__ import annotations

from datetime import date

from fastapi import Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.repositories.deliverable_repository import DeliverableRepository
from app.core.schemas.deliverable import DeliverableRead, DeliverableUpdate

VALID_STATUSES = {"Pending", "Submitted", "Delivered", "Approved", "Rejected"}


class DeliverableService:
    def __init__(self, db: Session):
        self.repository = DeliverableRepository(db)

    @staticmethod
    def _to_read(deliverable):
        return DeliverableRead(
            id=deliverable.id,
            group_id=deliverable.group_id,
            stage_id=deliverable.stage_id,
            stage_name=deliverable.stage.name,
            expected_date=deliverable.expected_date,
            status=deliverable.status,
        )

    def get_all(self, page: int = 1, page_size: int = 10) -> list[DeliverableRead]:
        deliverables = self.repository.get_all(page=page, page_size=page_size)
        return [self._to_read(d) for d in deliverables]

    def get_by_id(self, deliverable_id: int) -> DeliverableRead:
        deliverable = self.repository.get_by_id(deliverable_id)
        if deliverable is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail="Deliverable not found"
            )
        return self._to_read(deliverable)

    def update(self, data: DeliverableUpdate) -> DeliverableRead:
        deliverable = self.repository.get_by_id(data.id)
        if deliverable is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail="Deliverable not found"
            )

        update_data = data.model_dump(exclude_unset=True, exclude={"id"})

        if "status" in update_data and update_data["status"] not in VALID_STATUSES:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            )

        updated = self.repository.update(deliverable, update_data)
        return self._to_read(updated)

    def get_pending(self) -> list[DeliverableRead]:
        deliverables = self.repository.get_by_status("Pending")
        return [self._to_read(d) for d in deliverables]

    def get_overdue(self) -> list[DeliverableRead]:
        deliverables = self.repository.get_overdue(date.today())
        return [self._to_read(d) for d in deliverables]


def get_deliverable_service(db: Session = Depends(get_db)) -> DeliverableService:
    return DeliverableService(db)
