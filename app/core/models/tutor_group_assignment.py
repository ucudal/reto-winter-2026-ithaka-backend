from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class TutorGroupAssignment(Base):
    """One row per continuous period a tutor was assigned to a group."""
    __tablename__ = "tutor_group_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tutor: Mapped["Tutor"] = relationship(back_populates="assignments")
    group: Mapped["Group"] = relationship(back_populates="tutor_assignments")

    __table_args__ = (
        Index("ix_active_group_tutor_assignment", "group_id", "removed_at"),
        Index("ix_active_tutor_assignment", "tutor_id", "removed_at"),
    )
