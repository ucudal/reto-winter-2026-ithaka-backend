from __future__ import annotations
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class SupportMaterial(Base):
    #Material de apoyo general para todos los grupos de una etapa
    #De momento es un link

    __tablename__ = "support_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    stage_id: Mapped[int] = mapped_column(
        ForeignKey("stages.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    stage: Mapped["Stage"] = relationship(back_populates="support_materials")
