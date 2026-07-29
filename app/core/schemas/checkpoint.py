from datetime import date

from pydantic import BaseModel, ConfigDict


class CheckpointQuestion(BaseModel):
    id: int
    text: str
    answer: str | None = None



class CheckpointBase(BaseModel):
    group_id: int
    cohort_id: int
    title: str
    due_date: date
    status: str = "Pending"
    questions: list[CheckpointQuestion]


class CheckpointUpdateRequest(BaseModel):
    title: str | None = None
    due_date: date | None = None
    status: str | None = None
    questions: list[CheckpointQuestion] | None = None



class CheckpointRead(CheckpointBase):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int



class CheckpointResponseRead(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    checkpoint_id: int
    user_id: int
    role: str
    completed: bool
    answers: list[CheckpointQuestion]
    