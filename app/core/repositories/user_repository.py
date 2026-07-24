from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.enums import UserRole
from app.core.models.user import User


class UserRepository:
    """Capa de acceso a datos del modelo User."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[User]:
        stmt = select(User).order_by(User.id)
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        *,
        name: str,
        email: str,
        role: UserRole,
        password_hash: str,
    ) -> User:
        user = User(
            name=name,
            email=email,
            role=role,
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, *, name: str, email: str, role: UserRole) -> User:
        user.name = name
        user.email = email
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()