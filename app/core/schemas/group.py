from pydantic import BaseModel


class GroupUpsert(BaseModel):
    id: int | None = None
    name: str
    cohort_id: int
    current_stage_id: int | None = None
    idea: str = ""
    major: str | None = None
    status: str = "Active"
    student_ids: list[int]
    business_tutor_id: int | None = None
    technical_tutor_id: int | None = None


class GroupResponse(BaseModel):
    id: int
    name: str
    cohort_id: int
    current_stage_id: int | None
    idea: str | None
    major: str | None
    status: str
    business_tutor_id: int | None
    technical_tutor_id: int | None

    class Config:
        from_attributes = True


class GroupStageUpdate(BaseModel):
    stage_id: int
