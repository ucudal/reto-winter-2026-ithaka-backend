from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.repositories.user_repository import UserRepository
from app.core.schemas.user import UserCreate, UserRead
from app.core.security import get_current_user, require_roles
from app.core.services.auth_service import AuthService

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Devuelve el perfil del usuario autenticado."""
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
) -> list[User]:
    """Lista todos los usuarios. Solo para Coordinator."""
    return UserRepository(db).list_all()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
) -> User:
    """Crea un nuevo usuario. Solo para Coordinator."""
    return AuthService(db).create_user(data)