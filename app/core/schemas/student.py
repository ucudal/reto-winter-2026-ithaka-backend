from pydantic import BaseModel, ConfigDict, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None 


class StudentUpdate(StudentBase):
    id: int | None = None


class StudentRead(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)