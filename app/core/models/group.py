from __future__ import annotations
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class Group(Base):

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    cohort_id: Mapped[int] = mapped_column(
        ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False
    )
    current_stage_id: Mapped[int | None] = mapped_column(
        ForeignKey("stages.id", ondelete="SET NULL"), nullable=True
    )
    idea: Mapped[str | None] = mapped_column(Text, nullable=True)

    cohort: Mapped["Cohort"] = relationship(back_populates="groups")

    current_stage: Mapped["Stage | None"] = relationship(back_populates="groups")
    students: Mapped[list["Student"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
    deliverables: Mapped[list["Deliverable"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
