from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    cohort_id: int
    current_stage_id: int | None = None
    idea: str = ""
    major: str | None = None
    business_tutor_id: int | None = None
    technical_tutor_id: int | None = None


class GroupUpdate(BaseModel):
    name: str
    cohort_id: int
    current_stage_id: int | None = None
    idea: str = ""
    major: str | None = None
    status: str = "Active"
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