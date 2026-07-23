from __future__ import annotations
 
from datetime import date
 
from pydantic import BaseModel, ConfigDict
 
 
class DeliverableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    id: int | None = None
    group_id: int
    stage_id: int
    expected_date: date
    status: str
 
 
class DeliverableUpdate(BaseModel):
    expected_date: date | None = None
    status: str | None = None