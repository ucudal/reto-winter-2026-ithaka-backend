"""Casos exitosos: con el rol correcto, el endpoint responde 200 de verdad.

Los tests de `test_permissions.py` solo verifican que no haya 403. Aca cerramos
el otro lado: que el guard no este bloqueando de mas.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.core.services.dashboard_service import get_dashboard_service
from app.api.materials_api import get_support_material_service
from app.api.tutors_api import get_tutor_service
from app.main import app as fastapi_app

TODOS = ("coordinator", "business_tutor", "technical_tutor", "student")
TUTORES = ("coordinator", "business_tutor", "technical_tutor")
SOLO_COORD = ("coordinator",)

# (url, roles que deben recibir 200)
LECTURAS = [
    ("/api/users/me", TODOS),
    ("/api/users", SOLO_COORD),
    ("/api/cohorts", TODOS),
    ("/api/cohorts/1", TODOS),
    ("/api/cohorts/1/groups", TODOS),
    ("/api/cohorts/1/stages", TODOS),
    ("/api/groups", TODOS),
    ("/api/groups/1", TODOS),
    ("/api/groups/1/students", TODOS),
    ("/api/groups/1/meetings", TODOS),
    ("/api/groups/1/documents", TODOS),
    ("/api/groups/1/meetings/total-hours", TODOS),
    ("/api/students", TUTORES),
    ("/api/students/1", TODOS),
    ("/api/tutors", TODOS),
    ("/api/tutors/1", TODOS),
    ("/api/tutors/1/groups", TUTORES),
    ("/api/stages", TODOS),
    ("/api/stages/1/expected-deliverables", TODOS),
    ("/api/deliverables", TODOS),
    ("/api/deliverables/1", TODOS),
    ("/api/deliverables/pending", TUTORES),
    ("/api/deliverables/overdue", TUTORES),
    ("/api/deliverables/1/comments", TODOS),
    ("/api/deliverables/1/documents", TODOS),
    ("/api/materials", TODOS),
    ("/api/checkpoints", TODOS),
    ("/api/checkpoints/my-pending", TODOS),
    ("/api/materials/1", TODOS),
    ("/api/meetings", TODOS),
    ("/api/meetings/1", TODOS),
]

CASOS = [
    pytest.param(url, rol, id=f"{url}-{rol}")
    for url, permitidos in LECTURAS
    for rol in permitidos
]


@pytest.mark.parametrize(("url", "rol"), CASOS)
def test_acceso_autorizado_devuelve_200(client_con_datos, headers, url, rol):
    resp = client_con_datos.get(url, headers=headers[rol])
    assert resp.status_code == 200, f"{rol} en {url}: {resp.status_code} {resp.text[:200]}"


@pytest.mark.xfail(
    reason="BUG: GroupService.get_group_deliverables devuelve el ORM crudo y "
           "DeliverableRead exige `stage_name`. Rompe con 500 tambien en PostgreSQL. "
           "DeliverableService si lo completa (stage_name=deliverable.stage.name).",
    strict=True,
)
@pytest.mark.parametrize("rol", TODOS)
def test_entregables_del_grupo_devuelve_200(client_con_datos, headers, rol):
    resp = client_con_datos.get("/api/groups/1/deliverables", headers=headers[rol])
    assert resp.status_code == 200, resp.text


def test_users_me_devuelve_al_usuario_del_token(client_con_datos, headers):
    for rol, email in [
        ("coordinator", "coord@ucu.edu.uy"),
        ("business_tutor", "maria@ucu.edu.uy"),
        ("student", "ana@ucu.edu.uy"),
    ]:
        resp = client_con_datos.get("/api/users/me", headers=headers[rol])
        assert resp.status_code == 200
        assert resp.json()["email"] == email


@pytest.fixture
def materiales_mockeado():
    """Los repositorios usan `pg_get_serial_sequence` (PostgreSQL) al escribir,
    asi que en SQLite mockeamos el service para poder testear el guard."""
    mock = MagicMock()
    mock.upsert_material.return_value = {
        "id": 99, "stage_id": 1, "title": "Guia de validacion",
        "url": "https://drive.google.com/guia",
    }
    mock.delete_material.return_value = None
    fastapi_app.dependency_overrides[get_support_material_service] = lambda: mock
    yield mock
    fastapi_app.dependency_overrides.pop(get_support_material_service, None)


PAYLOAD_MATERIAL = {
    "stage_id": 1,
    "title": "Guia de validacion",
    "url": "https://drive.google.com/guia",
}


def test_escritura_autorizada_llega_al_service(client_con_datos, headers, materiales_mockeado):
    resp = client_con_datos.put(
        "/api/materials", headers=headers["coordinator"], json=PAYLOAD_MATERIAL
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == 99
    materiales_mockeado.upsert_material.assert_called_once()


@pytest.mark.parametrize("rol", ["student"])
def test_escritura_denegada_no_llega_al_service(
    client_con_datos, headers, materiales_mockeado, rol
):
    """Lo importante no es solo el 403: la logica de negocio no debe ejecutarse."""
    resp = client_con_datos.put("/api/materials", headers=headers[rol], json=PAYLOAD_MATERIAL)
    assert resp.status_code == 403
    materiales_mockeado.upsert_material.assert_not_called()


def test_borrado_denegado_no_llega_al_service(client_con_datos, headers, materiales_mockeado):
    for rol in ("business_tutor", "technical_tutor", "student"):
        resp = client_con_datos.delete("/api/materials/1", headers=headers[rol])
        assert resp.status_code == 403, rol
    materiales_mockeado.delete_material.assert_not_called()


def test_borrado_autorizado_llega_al_service(client_con_datos, headers, materiales_mockeado):
    resp = client_con_datos.delete("/api/materials/1", headers=headers["coordinator"])
    assert resp.status_code == 204
    materiales_mockeado.delete_material.assert_called_once()


# --- endpoints que dependen de PostgreSQL: se mockea el service ----------
# `/api/dashboard/summary` y la capacidad de tutores usan features de Postgres
# (operador JSONB `@>`, datetimes con timezone) que SQLite no soporta. Para
# testear la capa de autorizacion mockeamos el service: lo que se valida aca es
# el guard, no la query.

@pytest.fixture
def dashboard_mockeado():
    mock = MagicMock()
    mock.get_summary.return_value = {
        "active_groups": 1,
        "active_tutors": 2,
        "groups_by_stage": [],
        "groups_by_cohort": [],
        "hours_by_group": [],
        "capacity": {"total_available_hours": 0, "total_used_hours": 0, "usage_percentage": 0},
        "pending_deliverables": 1,
        "alerts": [],
    }
    fastapi_app.dependency_overrides[get_dashboard_service] = lambda: mock
    yield mock
    fastapi_app.dependency_overrides.pop(get_dashboard_service, None)


@pytest.mark.parametrize("rol", TUTORES)
def test_dashboard_devuelve_200_con_service_mockeado(
    client_con_datos, headers, dashboard_mockeado, rol
):
    resp = client_con_datos.get("/api/dashboard/summary", headers=headers[rol])
    assert resp.status_code == 200
    assert resp.json()["active_groups"] == 1


def test_dashboard_no_llama_al_service_si_el_rol_no_alcanza(
    client_con_datos, headers, dashboard_mockeado
):
    """El guard corta antes: la logica de negocio ni se ejecuta."""
    resp = client_con_datos.get("/api/dashboard/summary", headers=headers["student"])
    assert resp.status_code == 403
    dashboard_mockeado.get_summary.assert_not_called()


def test_dashboard_no_llama_al_service_sin_token(client_con_datos, dashboard_mockeado):
    resp = client_con_datos.get("/api/dashboard/summary")
    assert resp.status_code == 401
    dashboard_mockeado.get_summary.assert_not_called()


@pytest.fixture
def tutor_service_mockeado():
    """`tutors_api` expone el service via `Depends(get_tutor_service)`."""
    mock = MagicMock()
    mock.get_tutor_capacity.return_value = {
        "tutor_id": 1, "max_capacity": 88, "assigned_hours": 0,
        "available_hours": 88, "usage_percentage": 0, "overloaded": False, "groups": [],
    }
    mock.list_overloaded.return_value = []
    fastapi_app.dependency_overrides[get_tutor_service] = lambda: mock
    yield mock
    fastapi_app.dependency_overrides.pop(get_tutor_service, None)


@pytest.mark.parametrize("rol", TUTORES)
def test_capacidad_de_tutor_devuelve_200_con_service_mockeado(
    client_con_datos, headers, tutor_service_mockeado, rol
):
    resp = client_con_datos.get("/api/tutors/1/capacity", headers=headers[rol])
    assert resp.status_code == 200
    assert resp.json()["tutor_id"] == 1


def test_capacidad_de_tutor_denegada_al_alumno(
    client_con_datos, headers, tutor_service_mockeado
):
    resp = client_con_datos.get("/api/tutors/1/capacity", headers=headers["student"])
    assert resp.status_code == 403
    tutor_service_mockeado.get_tutor_capacity.assert_not_called()


def test_tutores_sobrecargados_solo_para_coordinador(
    client_con_datos, headers, tutor_service_mockeado
):
    ok = client_con_datos.get("/api/tutors/overloaded", headers=headers["coordinator"])
    assert ok.status_code == 200

    for rol in ("business_tutor", "technical_tutor", "student"):
        assert client_con_datos.get(
            "/api/tutors/overloaded", headers=headers[rol]
        ).status_code == 403