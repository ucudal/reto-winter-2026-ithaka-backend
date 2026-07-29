"""Validaciones: que el orden auth -> permisos -> validacion de payload sea el correcto.

Un 422 antes de un 401 seria una fuga de informacion: le confirma a un anonimo
que el endpoint existe y que forma tiene su payload.
"""
from __future__ import annotations

import pytest

PAYLOAD_INVALIDO = {"campo_que_no_existe": True}


@pytest.mark.parametrize(
    ("metodo", "url"),
    [
        ("PUT", "/api/cohorts"),
        ("PUT", "/api/groups"),
        ("PUT", "/api/tutors"),
        ("PUT", "/api/stages"),
        ("PUT", "/api/students"),
        ("PUT", "/api/materials"),
        ("PUT", "/api/meetings"),
        ("PUT", "/api/deliverables"),
        ("POST", "/api/users"),
    ],
)
def test_sin_token_da_401_y_no_422(client, metodo, url):
    """La autenticacion corre antes que la validacion del body."""
    resp = client.request(metodo, url, json=PAYLOAD_INVALIDO)
    assert resp.status_code == 401, (
        f"{metodo} {url} devolvio {resp.status_code}: valida el payload antes de "
        f"pedir token, lo que revela la forma de la API a un anonimo"
    )


@pytest.mark.parametrize(
    ("metodo", "url"),
    [
        ("PUT", "/api/cohorts"),
        ("PUT", "/api/groups"),
        ("PUT", "/api/tutors"),
        ("PUT", "/api/stages"),
        ("PUT", "/api/students"),
        ("POST", "/api/users"),
    ],
)
def test_rol_insuficiente_da_403_y_no_422(client, headers, metodo, url):
    """La autorizacion tambien corre antes que la validacion del body."""
    resp = client.request(metodo, url, headers=headers["student"], json=PAYLOAD_INVALIDO)
    assert resp.status_code == 403


def test_payload_invalido_con_rol_correcto_da_422(client, headers):
    """Recien con permisos suficientes aparece el error de validacion."""
    resp = client.post("/api/users", headers=headers["coordinator"], json=PAYLOAD_INVALIDO)
    assert resp.status_code == 422


def test_password_corta_es_rechazada(client, headers):
    resp = client.post(
        "/api/users",
        headers=headers["coordinator"],
        json={"name": "Test", "email": "t@ucu.edu.uy", "role": "Student", "password": "corta"},
    )
    assert resp.status_code == 422


def test_rol_inexistente_es_rechazado(client, headers):
    resp = client.post(
        "/api/users",
        headers=headers["coordinator"],
        json={"name": "Test", "email": "t@ucu.edu.uy", "role": "SuperAdmin", "password": "password123"},
    )
    assert resp.status_code == 422


def test_email_duplicado_da_409(client, headers):
    resp = client.post(
        "/api/users",
        headers=headers["coordinator"],
        json={
            "name": "Otro Coord",
            "email": "coord@ucu.edu.uy",
            "role": "Coordinator",
            "password": "password123",
        },
    )
    assert resp.status_code == 409


def test_usuario_creado_puede_loguearse(client, headers):
    """El alta guarda un hash valido, no un placeholder."""
    alta = client.post(
        "/api/users",
        headers=headers["coordinator"],
        json={"name": "Nuevo", "email": "nuevo@ucu.edu.uy", "role": "Student", "password": "password123"},
    )
    assert alta.status_code == 201

    login = client.post(
        "/api/auth/login", json={"email": "nuevo@ucu.edu.uy", "password": "password123"}
    )
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "Student"


def test_alta_de_usuario_no_devuelve_el_password(client, headers):
    resp = client.post(
        "/api/users",
        headers=headers["coordinator"],
        json={"name": "Nuevo", "email": "nuevo2@ucu.edu.uy", "role": "Student", "password": "password123"},
    )
    assert "password" not in resp.json()
    assert "password_hash" not in resp.text


def test_id_no_numerico_da_422_solo_con_token(client, headers):
    """Sin token, ni siquiera se llega a parsear el path param."""
    assert client.get("/api/cohorts/abc").status_code == 401
    assert client.get("/api/cohorts/abc", headers=headers["coordinator"]).status_code == 422
