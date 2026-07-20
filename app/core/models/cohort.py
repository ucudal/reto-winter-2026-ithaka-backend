from __future__ import annotations
from datetime import date
from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base


class Cohort(Base):

    __tablename__ = "cohorts"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    groups: Mapped[list["Group"]] = relationship(
        back_populates="cohort", cascade="all, delete-orphan"
    )
    stages: Mapped[list["Stage"]] = relationship(
        back_populates="cohort", cascade="all, delete-orphan"
    )
