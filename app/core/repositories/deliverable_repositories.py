from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.deliverable import Deliverable


def get_all_deliverables(db: Session) -> list[Deliverable]:
    return list(db.scalars(select(Deliverable)))


def get_deliverable_by_id(db: Session, deliverable_id: int) -> Deliverable | None:
    return db.get(Deliverable, deliverable_id)


def update_deliverable(db: Session, deliverable: Deliverable, data: dict) -> Deliverable:
    for field, value in data.items():
        setattr(deliverable, field, value)
    db.commit()
    db.refresh(deliverable)
    return deliverable


def get_deliverables_by_status(db: Session, status: str) -> list[Deliverable]:
    return list(db.scalars(select(Deliverable).where(Deliverable.status == status)))


def get_overdue_deliverables(db: Session, today: date, status: str = "Pending") -> list[Deliverable]:
    return list(
        db.scalars(
            select(Deliverable).where(
                Deliverable.status == status,
                Deliverable.expected_date < today,
            )
        )
    )