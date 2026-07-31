from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.models.enums import UserRole
from app.core.schemas.student import StudentRead
from app.core.schemas.tutor import TutorRead


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(UserBase):
    pass


class UserSelfUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    student: StudentRead | None = None
    tutor: TutorRead | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    id: int
    name: str
    role: UserRole
    student: StudentRead | None = None
    tutor: TutorRead | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    token: str
    user: LoginUser


class PaginatedUserResponse(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    page_size: int