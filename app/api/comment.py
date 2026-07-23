from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tutor_id: int
    deliverable_id: int
    content: str


class CommentCreateRequest(BaseModel):
    tutor_id: int
    deliverable_id: int
    content: str