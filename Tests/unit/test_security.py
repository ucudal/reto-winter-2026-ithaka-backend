from __future__ import annotations

from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.models.enums import UserRole
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)


# ---------- hash_password / verify_password ----------

def test_hash_password_genera_hash_distinto_al_original():
    hashed = hash_password("secret123")
    assert hashed != "secret123"


def test_verify_password_correcta():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_password_incorrecta():
    hashed = hash_password("secret123")
    assert verify_password("otra_password", hashed) is False


def test_verify_password_hash_corrupto_devuelve_false():
    assert verify_password("secret123", "esto-no-es-un-hash") is False


# ---------- create_access_token (generación de JWT) ----------

def test_create_access_token_incluye_subject_correcto():
    token = create_access_token(subject="1")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "1"
    assert "exp" in payload


# ---------- get_current_user ----------

def test_get_current_user_sin_credenciales_tira_401():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None, db=None)
    assert exc_info.value.status_code == 401


def test_get_current_user_token_invalido_tira_401(mock_db):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="esto.no.es.un.jwt"
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=mock_db)
    assert exc_info.value.status_code == 401


def test_get_current_user_token_expirado_tira_401(mock_db):
    token_expirado = create_access_token(
        subject="1", expires_delta=timedelta(seconds=-10)
    )
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_expirado
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=mock_db)
    assert exc_info.value.status_code == 401


def test_get_current_user_devuelve_usuario_autenticado(mock_db, sample_user, mocker):
    mocker.patch(
        "app.core.security.UserRepository.get_by_id",
        return_value=sample_user,
    )
    token = create_access_token(subject=str(sample_user.id))
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    result = get_current_user(credentials=credentials, db=mock_db)

    assert result.id == sample_user.id
    assert result.email == sample_user.email


def test_get_current_user_usuario_no_existe_tira_401(mock_db, mocker):
    mocker.patch(
        "app.core.security.UserRepository.get_by_id",
        return_value=None,
    )
    token = create_access_token(subject="999")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials, db=mock_db)
    assert exc_info.value.status_code == 401


# ---------- require_roles (permisos por rol) ----------

def test_require_roles_con_rol_correcto_deja_pasar(sample_coordinator):
    dependency = require_roles(UserRole.COORDINATOR)
    result = dependency(current_user=sample_coordinator)
    assert result == sample_coordinator


def test_require_roles_con_rol_incorrecto_tira_403(sample_user):
    dependency = require_roles(UserRole.COORDINATOR)
    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=sample_user)
    assert exc_info.value.status_code == 403