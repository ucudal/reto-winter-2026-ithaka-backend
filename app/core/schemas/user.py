from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.models.enums import UserRole


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    id: int
    name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    token: str
    user: LoginUser