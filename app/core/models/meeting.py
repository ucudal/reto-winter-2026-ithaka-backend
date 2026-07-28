from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base


class MeetingStatus(str, Enum):
    SCHEDULED = "Scheduled"
    HELD = "Held"
    CANCELLED = "Cancelled"


class Meeting(Base):

    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    # Lista de IDs de tutores: [8, 14, ...] — una reunión puede tener uno o más tutores
    tutor_ids: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[MeetingStatus] = mapped_column(
        SAEnum(MeetingStatus, name="meeting_status", native_enum=False, length=20),
        nullable=False,
        default=MeetingStatus.SCHEDULED,
        server_default=MeetingStatus.SCHEDULED.value,
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Lista de asistencia: [{"student_id": 101, "attended": true}, ...]
    participants: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    # Resumen corto cargado a mano por el tutor. Auto-generación por IA queda para
    # una evolución futura, no MVP.
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    hours_spent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    # Lista de links: [{"type": "Drive", "url": "..."}]
    links: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)

    group: Mapped["Group"] = relationship(back_populates="meetings")