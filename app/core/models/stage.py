from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base


class Stage(Base):

    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    cohort_id: Mapped[int] = mapped_column(
        ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    # Lista de fechas clave de la etapa
    key_dates: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    
    cohort: Mapped["Cohort"] = relationship(back_populates="stages")
    groups: Mapped[list["Group"]] = relationship(back_populates="current_stage")
    deliverables: Mapped[list["Deliverable"]] = relationship(back_populates="stage")
    
    #Cada etapa puede tener materiales de apoyo
    support_materials: Mapped[list["SupportMaterial"]] = relationship(
        back_populates="stage", cascade="all, delete-orphan"
    )
