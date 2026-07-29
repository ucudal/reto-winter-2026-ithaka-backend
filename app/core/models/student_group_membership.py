from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class StudentGroupMembership(Base):
    """One row per continuous period a student belonged to a group."""
    __tablename__ = "student_group_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped["Student"] = relationship(back_populates="memberships")
    group: Mapped["Group"] = relationship(back_populates="student_memberships")

    __table_args__ = (
        Index("ix_active_group_membership", "group_id", "left_at"),
        Index("ix_active_student_membership", "student_id", "left_at"),
    )
