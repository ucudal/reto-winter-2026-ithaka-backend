from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.repositories.user_repository import UserRepository
from app.core.schemas.user import UserCreate, UserRead, UserUpdate
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


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
) -> User:
    """Actualiza un usuario. Solo para Coordinator."""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    existing_user = repo.get_by_email(data.email)
    if existing_user is not None and existing_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    return repo.update(user, name=data.name, email=data.email, role=data.role)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
) -> None:
    """Elimina un usuario. Solo para Coordinator."""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    repo.delete(user)