from __future__ import annotations
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.base import Base
from app.core.models.enums import DocumentPlatform, EntityType


class Document(Base):
    # Relación polimórfica: un documento puede pertenecer a un Group,
    # Meeting, Deliverable o SupportMaterial, identificado por entity_type + entity_id.

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[EntityType] = mapped_column(
        SAEnum(EntityType, name="entity_type"), nullable=False
    )
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    platform: Mapped[DocumentPlatform] = mapped_column(
        SAEnum(DocumentPlatform, name="document_platform"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
