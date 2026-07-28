from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.db.base import Base
from app.core.models.enums import CheckpointStatus


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[CheckpointStatus] = mapped_column(
        SAEnum(CheckpointStatus, name="checkpoint_status"),
        nullable=False,
        default=CheckpointStatus.OPEN,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    group: Mapped["Group"] = relationship(back_populates="checkpoints")
    responses: Mapped[list["CheckpointResponse"]] = relationship(
        back_populates="checkpoint", cascade="all, delete-orphan"
    )
    