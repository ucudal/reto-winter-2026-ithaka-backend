from pydantic import BaseModel, ConfigDict, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None 


class StudentUpsert(StudentBase):
    id: int | None = None
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None


class StudentRead(StudentBase):
    id: int
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
