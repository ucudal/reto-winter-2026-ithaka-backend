from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base


class Checkpoint(Base):

    __tablename__ = "checkpoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"), nullable=False
    )
    cohort_id: Mapped[int] = mapped_column(
        ForeignKey("cohorts.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Pending")
    questions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


    group = relationship("Group", back_populates="checkpoints")
    cohort = relationship("Cohort", back_populates="checkpoints")
