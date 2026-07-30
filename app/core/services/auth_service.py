from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models.user import User
from app.core.repositories.user_repository import UserRepository
from app.core.schemas.user import UserCreate
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthService:
    """Logica de autenticacion y gestion de usuarios."""

    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def authenticate(self, email: str, password: str) -> User:
        user = self.repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def login(self, email: str, password: str) -> tuple[User, str]:
        """Autentica y devuelve el usuario junto con un token firmado."""
        user = self.authenticate(email, password)
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        token = create_access_token(
            subject=str(user.id), 
            extra_claims={
                "role": role_str, 
                "name": user.name, 
                "email": user.email})
        return user, token

    def create_user(self, data: UserCreate) -> User:
        if self.repository.get_by_email(data.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        return self.repository.create(
            name=data.name,
            email=data.email,
            role=data.role,
            password_hash=hash_password(data.password),
        )