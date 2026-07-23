from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.core.models.enums import TutorRole


class TutorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: TutorRole
    specialty: str | None
    max_capacity: int
    availability: str | None
    status: str


class TutorUpdateRequest(BaseModel):
    name: str
    role: TutorRole
    specialty: str | None = None
    max_capacity: int
    availability: str | None = None
    status: str = "Active"


class TutorGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str
    cohort_id: int


class TutorCapacityRead(BaseModel):
    tutor_id: int
    max_capacity: int
    assigned_hours: float
    available_hours: float
    usage_percentage: float
    overloaded: bool