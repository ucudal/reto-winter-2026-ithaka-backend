"""Pruebas unitarias del modulo `app/core/security.py`.

Aca no se levanta la app ni se toca la base: las dependencias externas
(el repositorio de usuarios) se mockean. El objetivo es cubrir cada rama
del modulo, incluidas las de error.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException

from app.core.models.enums import UserRole
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_authenticated,
    require_coordinator,
    require_roles,
    require_tutor_or_coordinator,
    verify_password,
)
from tests.conf_test import SECRET


def _credenciales(token: str):
    """Imita el objeto que arma HTTPBearer."""
    cred = MagicMock()
    cred.credentials = token
    return cred


def _usuario(rol: UserRole = UserRole.COORDINATOR, id_: int = 1):
    u = MagicMock()
    u.id = id_
    u.role = rol
    return u


# --- hashing -------------------------------------------------------------

def test_hash_password_genera_hash_bcrypt():
    h = hash_password("password123")
    assert h.startswith("$2b$")
    assert h != "password123"


def test_hash_password_usa_salt_distinto_cada_vez():
    a = hash_password("password123")
    b = hash_password("password123")
    assert a != b
    assert verify_password("password123", a)
    assert verify_password("password123", b)


def test_verify_password_correcta():
    assert verify_password("password123", hash_password("password123")) is True


def test_verify_password_incorrecta():
    assert verify_password("otra-cosa", hash_password("password123")) is False


def test_verify_password_con_hash_corrupto_no_explota():
    """Un hash mal formado en la base debe tratarse como fallo, no como 500."""
    assert verify_password("password123", "esto-no-es-un-hash") is False


def test_verify_password_con_hash_vacio():
    assert verify_password("password123", "") is False


# --- creacion de token ---------------------------------------------------

def test_create_access_token_incluye_sub_y_exp():
    token = create_access_token(subject="7")
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert payload["sub"] == "7"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_create_access_token_agrega_extra_claims():
    token = create_access_token(subject="7", extra_claims={"role": "Coordinator"})
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert payload["role"] == "Coordinator"


def test_create_access_token_respeta_expires_delta():
    token = create_access_token(subject="7", expires_delta=timedelta(seconds=1))
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    faltan = payload["exp"] - datetime.now(timezone.utc).timestamp()
    assert faltan < 5


def test_token_creado_no_es_legible_con_otra_clave():
    token = create_access_token(subject="7")
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(token, "clave-equivocada", algorithms=["HS256"])


# --- get_current_user ----------------------------------------------------

def test_get_current_user_sin_credenciales():
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, db=MagicMock())
    assert exc.value.status_code == 401


def test_get_current_user_token_invalido():
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=_credenciales("no-es-un-jwt"), db=MagicMock())
    assert exc.value.status_code == 401


def test_get_current_user_sin_claim_sub():
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, SECRET, algorithm="HS256"
    )
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=_credenciales(token), db=MagicMock())
    assert exc.value.status_code == 401


def test_get_current_user_con_sub_no_numerico():
    token = jwt.encode(
        {"sub": "no-es-un-id", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        SECRET, algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=_credenciales(token), db=MagicMock())
    assert exc.value.status_code == 401


@patch("app.core.security.UserRepository")
def test_get_current_user_usuario_inexistente(repo_mock):
    repo_mock.return_value.get_by_id.return_value = None
    token = create_access_token(subject="999")
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=_credenciales(token), db=MagicMock())
    assert exc.value.status_code == 401


@patch("app.core.security.UserRepository")
def test_get_current_user_devuelve_el_usuario(repo_mock):
    esperado = _usuario()
    repo_mock.return_value.get_by_id.return_value = esperado
    token = create_access_token(subject="1")

    obtenido = get_current_user(credentials=_credenciales(token), db=MagicMock())

    assert obtenido is esperado
    repo_mock.return_value.get_by_id.assert_called_once_with(1)


@patch("app.core.security.UserRepository")
def test_get_current_user_busca_por_el_sub_del_token(repo_mock):
    """El id consultado sale del token, no de otro lado."""
    repo_mock.return_value.get_by_id.return_value = _usuario(id_=42)
    get_current_user(credentials=_credenciales(create_access_token(subject="42")), db=MagicMock())
    repo_mock.return_value.get_by_id.assert_called_once_with(42)


def test_get_current_user_respuesta_401_trae_www_authenticate():
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, db=MagicMock())
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"


# --- require_roles -------------------------------------------------------

def test_require_roles_deja_pasar_al_rol_permitido():
    dep = require_roles(UserRole.COORDINATOR)
    user = _usuario(UserRole.COORDINATOR)
    assert dep(current_user=user) is user


def test_require_roles_rechaza_al_rol_no_permitido():
    dep = require_roles(UserRole.COORDINATOR)
    with pytest.raises(HTTPException) as exc:
        dep(current_user=_usuario(UserRole.STUDENT))
    assert exc.value.status_code == 403


def test_require_roles_acepta_varios_roles():
    dep = require_roles(UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR)
    assert dep(current_user=_usuario(UserRole.BUSINESS_TUTOR))
    assert dep(current_user=_usuario(UserRole.TECHNICAL_TUTOR))
    with pytest.raises(HTTPException):
        dep(current_user=_usuario(UserRole.COORDINATOR))


@pytest.mark.parametrize(
    "rol", [UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR, UserRole.STUDENT]
)
def test_require_coordinator_rechaza_todo_lo_que_no_sea_coordinador(rol):
    with pytest.raises(HTTPException) as exc:
        require_coordinator(current_user=_usuario(rol))
    assert exc.value.status_code == 403


@pytest.mark.parametrize(
    "rol", [UserRole.COORDINATOR, UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR]
)
def test_require_tutor_or_coordinator_acepta_coordinador_y_tutores(rol):
    assert require_tutor_or_coordinator(current_user=_usuario(rol))


def test_require_tutor_or_coordinator_rechaza_alumno():
    with pytest.raises(HTTPException) as exc:
        require_tutor_or_coordinator(current_user=_usuario(UserRole.STUDENT))
    assert exc.value.status_code == 403


# --- regresion -----------------------------------------------------------

@pytest.mark.parametrize(
    "guard", [require_authenticated, require_coordinator, require_tutor_or_coordinator]
)
def test_los_guards_son_dependencias_no_fabricas(guard):
    """Regresion: si vuelven a ser fabricas, `Depends(guard)` no valida nada.

    Una fabrica devuelve otra funcion al llamarla. FastAPI no resuelve eso de
    forma recursiva: usaria el valor devuelto como resultado y el endpoint
    quedaria abierto. El guard tiene que aceptar `current_user`.
    """
    import inspect

    parametros = inspect.signature(guard).parameters
    assert "current_user" in parametros or "credentials" in parametros, (
        f"{guard} no recibe el usuario: parece una fabrica, "
        f"y Depends() sobre una fabrica deja el endpoint sin proteger"
    )


def test_require_authenticated_es_get_current_user():
    assert require_authenticated is get_current_user