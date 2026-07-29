from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.models.enums import UserRole
from app.core.models.user import User


class UserRepository:
    """Capa de acceso a datos del modelo User."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(
                joinedload(User.student),
                joinedload(User.tutor)
            )
            .where(User.id == user_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .options(
                joinedload(User.student),
                joinedload(User.tutor)
            )
            .where(User.email == email)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self, *, role: UserRole | None = None, name_search: str | None = None, page: int = 1, page_size: int = 10) -> tuple[list[User], int]:
        # Get total count
        count_stmt = select(User)
        if role is not None:
            count_stmt = count_stmt.where(User.role == role)
        if name_search is not None:
            count_stmt = count_stmt.where(User.name.ilike(f"%{name_search}%"))
        total = self.db.execute(count_stmt).scalars().count()
        
        # Get paginated items
        stmt = select(User)
        if role is not None:
            stmt = stmt.where(User.role == role)
        if name_search is not None:
            stmt = stmt.where(User.name.ilike(f"%{name_search}%"))
        
        stmt = stmt.order_by(User.id)
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        
        return items, total

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