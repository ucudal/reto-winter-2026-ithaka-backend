from __future__ import annotations
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base
from app.core.models.enums import TutorRole


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[TutorRole] = mapped_column(
        SAEnum(TutorRole, name="tutor_role"), nullable=False
    )
    specialty: Mapped[str | None] = mapped_column(String(200), nullable=True)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    availability: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Active")

    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="tutor", cascade="all, delete-orphan"
    )
    
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="tutor")
    comments: Mapped[list["Comment"]] = relationship(back_populates="tutor")
