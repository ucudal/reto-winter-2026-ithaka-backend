from __future__ import annotations
from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class Deliverable(Base):

    __tablename__ = "deliverables"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    stage_id: Mapped[int] = mapped_column(
        ForeignKey("stages.id", ondelete="RESTRICT"), nullable=False
    )
    expected_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Pending")

    group: Mapped["Group"] = relationship(back_populates="deliverables")
    stage: Mapped["Stage"] = relationship(back_populates="deliverables")
    # documents se resuelven vía Document.entity_type='Deliverable' + entity_id (polimórfico)
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="deliverable", cascade="all, delete-orphan"
    )
