from datetime import date

from pydantic import BaseModel, ConfigDict


class StageBase(BaseModel):
    cohort_id: int
    name: str
    order: int
    key_dates: list[dict] | None = None


class StageUpsert(StageBase):
    id: int | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cohort_id": 2,
                "name": "Planning",
                "order": 1,
                "key_dates": [
                    {
                        "description": "Kickoff",
                        "date": "2026-07-22",
                    }
                ],
            }
        }
    )


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