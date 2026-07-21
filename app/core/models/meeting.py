from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class Meeting(Base):

    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Lista de IDs de participantes: [101, 102, ...]
    participants: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    hours_spent: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    # Lista de links: [{"type": "Drive", "url": "..."}]
    links: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)

    group: Mapped["Group"] = relationship(back_populates="meetings")
    tutor: Mapped["Tutor"] = relationship(back_populates="meetings")
