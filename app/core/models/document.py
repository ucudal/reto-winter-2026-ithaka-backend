from __future__ import annotations
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base
from app.core.models.enums import DocumentPlatform


class Document(Base):
    #De momento es un link

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    deliverable_id: Mapped[int] = mapped_column(
        ForeignKey("deliverables.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    platform: Mapped[DocumentPlatform] = mapped_column(
        SAEnum(DocumentPlatform, name="document_platform"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    deliverable: Mapped["Deliverable"] = relationship(back_populates="documents")
