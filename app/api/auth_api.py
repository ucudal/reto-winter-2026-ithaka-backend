from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.user import Token
from app.core.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Loguea con credenciales y devuelve un JWT.

    El campo ``username`` del formulario OAuth2 lleva el email del usuario.
    """
    token = AuthService(db).login(
        email=form_data.username,
        password=form_data.password,
    )
    return Token(access_token=token)