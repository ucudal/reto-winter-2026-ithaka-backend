from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from app.core.schemas.tutor import TutorRead
from app.core.schemas.stage import StageRead
from app.core.schemas.student import StudentRead
from app.core.schemas.cohort import CohortRead


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
    idea: str | None
    major: str | None
    status: str

    business_tutor: TutorRead | None = None
    technical_tutor: TutorRead | None = None
    current_stage: StageRead | None = None
    students: list[StudentRead] = []
    cohort: CohortRead | None = None

    model_config = ConfigDict(from_attributes=True)


class GroupStageUpdate(BaseModel):
    stage_id: int


class GroupTutorsUpdate(BaseModel):
    business_tutor_id: int | None = None
    technical_tutor_id: int | None = None
