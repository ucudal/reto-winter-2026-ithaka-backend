from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.core.models.enums import DocumentPlatform, EntityType


class DocumentBase(BaseModel):
    url: str
    platform: DocumentPlatform
    order: int = 0


class DocumentUpsertRequest(DocumentBase):
    id: int | None = None


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entity_type: EntityType
    entity_id: int