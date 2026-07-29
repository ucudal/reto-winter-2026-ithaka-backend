"""Tests del flujo de login y de la validacion del token."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from tests.conftest import PASSWORD, SECRET, USUARIOS


# --- login ---------------------------------------------------------------

def test_login_devuelve_token_y_usuario(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "coord@ucu.edu.uy", "password": PASSWORD},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"token", "user"}
    assert body["user"]["id"] > 0
    assert body["user"]["name"] == "Coord Ithaka"
    assert body["user"]["role"] == "Coordinator"
    assert isinstance(body["token"], str) and body["token"].count(".") == 2


@pytest.mark.parametrize("rol", list(USUARIOS))
def test_login_funciona_para_todos_los_roles(client, rol):
    _, email, esperado = USUARIOS[rol]
    resp = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == esperado.value


def test_login_password_incorrecta(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "coord@ucu.edu.uy", "password": "esta-no-es"},
    )
    assert resp.status_code == 401


def test_login_email_inexistente(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "nadie@ucu.edu.uy", "password": PASSWORD},
    )
    assert resp.status_code == 401


def test_login_no_filtra_si_el_email_existe(client):
    """El mensaje debe ser el mismo para password mala y email inexistente."""
    a = client.post("/api/auth/login", json={"email": "coord@ucu.edu.uy", "password": "mala"})
    b = client.post("/api/auth/login", json={"email": "nadie@ucu.edu.uy", "password": "mala"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()


def test_login_no_devuelve_el_password_hash(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "coord@ucu.edu.uy", "password": PASSWORD},
    )
    assert "password_hash" not in resp.text
    assert "password" not in resp.json()["user"]


def test_login_email_invalido_es_422(client):
    resp = client.post("/api/auth/login", json={"email": "no-es-un-email", "password": PASSWORD})
    assert resp.status_code == 422


# --- validacion del token ------------------------------------------------

def test_users_me_con_token_valido(client, headers):
    resp = client.get("/api/users/me", headers=headers["coordinator"])
    assert resp.status_code == 200
    assert resp.json()["email"] == "coord@ucu.edu.uy"


def test_sin_header_authorization(client):
    assert client.get("/api/users/me").status_code == 401


def test_token_basura(client):
    resp = client.get("/api/users/me", headers={"Authorization": "Bearer no-es-un-jwt"})
    assert resp.status_code == 401


def test_header_sin_bearer(client, tokens):
    resp = client.get("/api/users/me", headers={"Authorization": tokens["coordinator"]})
    assert resp.status_code == 401


def test_esquema_equivocado(client, tokens):
    resp = client.get("/api/users/me", headers={"Authorization": f"Basic {tokens['coordinator']}"})
    assert resp.status_code == 401


def test_token_firmado_con_otra_clave(client):
    falso = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "clave-equivocada",
        algorithm="HS256",
    )
    resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {falso}"})
    assert resp.status_code == 401


def test_token_vencido(client):
    vencido = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET,
        algorithm="HS256",
    )
    resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {vencido}"})
    assert resp.status_code == 401


def test_token_sin_claim_sub(client):
    sin_sub = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        SECRET,
        algorithm="HS256",
    )
    resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {sin_sub}"})
    assert resp.status_code == 401


def test_token_de_usuario_borrado(client):
    """Firma valida pero el `sub` no existe en la base."""
    fantasma = jwt.encode(
        {"sub": "999999", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        SECRET,
        algorithm="HS256",
    )
    resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {fantasma}"})
    assert resp.status_code == 401


def test_el_rol_sale_de_la_base_y_no_del_token(client):
    """Un token con claim `role` falseado no debe dar permisos de mas."""
    alumno = client.post(
        "/api/auth/login", json={"email": "ana@ucu.edu.uy", "password": PASSWORD}
    ).json()
    payload = jwt.decode(alumno["token"], SECRET, algorithms=["HS256"])
    payload["role"] = "Coordinator"
    manipulado = jwt.encode(payload, SECRET, algorithm="HS256")

    resp = client.get("/api/users", headers={"Authorization": f"Bearer {manipulado}"})
    assert resp.status_code == 403