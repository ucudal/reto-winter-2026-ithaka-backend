from __future__ import annotations
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class Comment(Base):
    # Comentario de un tutor en un entregable

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False
    )
    deliverable_id: Mapped[int] = mapped_column(
        ForeignKey("deliverables.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    tutor: Mapped["Tutor"] = relationship(back_populates="comments")
    deliverable: Mapped["Deliverable"] = relationship(back_populates="comments")