from __future__ import annotations
from datetime import date
from sqlalchemy import Date, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base
from app.core.models.enums import TutoringType


class Assignment(Base):
    #Conecta tutor con grupo

    __tablename__ = "assignments"

    __table_args__ = (
        # Evita asignar dos veces al mismo tutor al mismo grupo
        UniqueConstraint(
            "group_id", "tutor_id", "tutoring_type", name="uq_assignment_group_tutor_type"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False
    )
    tutoring_type: Mapped[TutoringType] = mapped_column(
        SAEnum(TutoringType, name="tutoring_type"), nullable=False
    )
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False)

    group: Mapped["Group"] = relationship(back_populates="assignments")
    tutor: Mapped["Tutor"] = relationship(back_populates="assignments")
