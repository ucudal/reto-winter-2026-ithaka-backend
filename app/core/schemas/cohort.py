from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class CohortBase(BaseModel):
    year: int
    semester: int
    start_date: date
    end_date: date | None = None
    status: str = "Active"
    notes: str | None = None


class CohortUpsertRequest(CohortBase):
    id: int | None = None


class CohortRead(CohortBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    group_count: int = 0


class CohortGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cohort_id: int
    status: str


class CohortStageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    order: int
    cohort_id: int
