from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base
from app.core.models.enums import RespondentType


class CheckpointResponse(Base):
    __tablename__ = "checkpoint_responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    checkpoint_id: Mapped[int] = mapped_column(
        ForeignKey("checkpoints.id", ondelete="CASCADE"), nullable=False
    )
    respondent_type: Mapped[RespondentType] = mapped_column(
        SAEnum(RespondentType, name="respondent_type"), nullable=False
    )
    respondent_id: Mapped[int] = mapped_column(nullable=False)
    attendance_ok: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    progress_ok: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    checkpoint: Mapped["Checkpoint"] = relationship(back_populates="responses")