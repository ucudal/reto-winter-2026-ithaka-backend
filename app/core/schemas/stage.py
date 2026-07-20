from datetime import date

from pydantic import BaseModel


class StageBase(BaseModel):
    cohort_id: int
    name: str
    order: int
    key_dates: list[dict] | None = None


class StageUpsert(StageBase):
    pass


class StageRead(StageBase):
    id: int

    class Config:
        from_attributes = True


class ExpectedDeliverableRead(BaseModel):
    id: int
    group_id: int
    expected_date: date
    status: str

    class Config:
        from_attributes = True