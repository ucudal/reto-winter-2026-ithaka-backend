from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.deliverable import Deliverable

# Un entregable se considera "vencido" si pasó su fecha esperada y no llegó a un
# estado final. Única definición de "vencido" en todo el backend — tanto el
# endpoint de entregables como el resumen del dashboard usan este mismo método.
DONE_STATUSES = ("Delivered", "Approved")


class DeliverableRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        group_id: int | None = None,
        stage_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[Deliverable]:
        statement = select(Deliverable)

        if group_id is not None:
            statement = statement.where(Deliverable.group_id == group_id)
        if stage_id is not None:
            statement = statement.where(Deliverable.stage_id == stage_id)
        if status is not None:
            statement = statement.where(Deliverable.status == status)

        statement = statement.order_by(Deliverable.id.asc())
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        return list(self.db.scalars(statement))

    def get_by_id(self, deliverable_id: int) -> Deliverable | None:
        return self.db.get(Deliverable, deliverable_id)

    def update(self, deliverable: Deliverable, data: dict) -> Deliverable:
        for field, value in data.items():
            setattr(deliverable, field, value)
        self.db.commit()
        self.db.refresh(deliverable)
        return deliverable

    def get_by_status(self, status: str) -> list[Deliverable]:
        return list(self.db.scalars(select(Deliverable).where(Deliverable.status == status)))

    def get_by_group(self, group_id: int) -> list[Deliverable]:
        return list(
            self.db.scalars(
                select(Deliverable)
                .where(Deliverable.group_id == group_id)
                .order_by(Deliverable.expected_date.asc())
            )
        )

    def get_overdue(
        self, today: date, group_ids: list[int] | None = None
    ) -> list[Deliverable]:
        if group_ids is not None and not group_ids:
            return []

        conditions = [
            Deliverable.expected_date < today,
            Deliverable.status.notin_(DONE_STATUSES),
        ]
        if group_ids is not None:
            conditions.append(Deliverable.group_id.in_(group_ids))

        return list(self.db.scalars(select(Deliverable).where(*conditions)))
