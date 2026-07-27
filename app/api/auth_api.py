from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.user import LoginRequest, LoginResponse, LoginUser, UserCreate
from app.core.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Loguea con email y contraseña (JSON) y devuelve un JWT con el usuario."""
    user, token = AuthService(db).login(email=data.email, password=data.password)
    return LoginResponse(token=token, user=LoginUser.model_validate(user))


@router.post("/register", response_model=LoginResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)) -> LoginResponse:
    """Registra un nuevo usuario y devuelve inmediatamente un JWT con sus datos de sesión."""
    auth_service = AuthService(db)
    user = auth_service.create_user(data)
    _, token = auth_service.login(email=data.email, password=data.password)
    return LoginResponse(token=token, user=LoginUser.model_validate(user))