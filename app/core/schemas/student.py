
from pydantic import BaseModel, ConfigDict, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None 
    is_graduation_project: bool = False
    linkedin_url: str | None = None


class StudentUpsert(StudentBase):
    id: int | None = None
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None
    is_graduation_project: bool = False
    linkedin_url: str | None = None


class StudentRead(StudentBase):
    id: int
    name: str
    email: EmailStr
    major: str | None = None
    group_id: int | None = None
    is_graduation_project: bool = False
    linkedin_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class StudentListResponse(BaseModel):
    items: list[StudentRead]
    total_items: int
    page: int
    page_size: int

