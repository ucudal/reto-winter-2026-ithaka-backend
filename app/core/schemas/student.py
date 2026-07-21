from pydantic import BaseModel, ConfigDict, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None 


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True) 