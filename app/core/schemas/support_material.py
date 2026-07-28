from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class SupportMaterialBase(BaseModel):
    stage_id: int
    title: str
    url: str


class SupportMaterialUpsertRequest(SupportMaterialBase):
    id: int | None = None


class SupportMaterialRead(SupportMaterialBase):
    model_config = ConfigDict(from_attributes=True)
    id: int