"""Red de seguridad contra endpoints nuevos sin proteger.

Estos tests recorren el OpenAPI de la app, asi que cubren automaticamente
cualquier router que se agregue en el futuro. Si alguien mergea un router sin
guard, esto falla en CI antes de que llegue a produccion.
"""
from __future__ import annotations

import pytest

from app.main import app as fastapi_app
from tests.test_permissions import MATRIZ

# Unicos endpoints que pueden responder sin token. Agregar algo aca tiene que
# ser una decision consciente y visible en el diff del PR.
PUBLICOS = {
    ("GET", "/health"),
    ("GET", "/health/db"),
    ("POST", "/api/auth/login"),
}

PLACEHOLDERS = {
    "{id}": "1",
    "{cohort_id}": "1",
    "{group_id}": "1",
    "{student_id}": "1",
    "{stage_id}": "1",
    "{deliverable_id}": "1",
    "{user_id}": "1",
    "{material_id}": "1",
    "{document_id}": "1",
    "{meeting_id}": "1",
}

METODOS = {"get", "post", "put", "patch", "delete"}


def _endpoints() -> list[tuple[str, str]]:
    salida = []
    for path, ops in fastapi_app.openapi()["paths"].items():
        for metodo in ops:
            if metodo in METODOS:
                salida.append((metodo.upper(), path))
    return sorted(salida)


def _concreta(path: str) -> str:
    for ph, valor in PLACEHOLDERS.items():
        path = path.replace(ph, valor)
    return path


TODOS_LOS_ENDPOINTS = _endpoints()


@pytest.mark.parametrize(
    ("metodo", "path"), TODOS_LOS_ENDPOINTS, ids=lambda v: str(v)
)
def test_todo_endpoint_no_publico_exige_token(client, metodo, path):
    """Sin header Authorization, todo endpoint tiene que responder 401."""
    if (metodo, path) in PUBLICOS:
        pytest.skip("endpoint publico por decision explicita")

    url = _concreta(path)
    assert "{" not in url, (
        f"falta un placeholder para {path}: agregalo al dict PLACEHOLDERS"
    )

    resp = client.request(metodo, url, json={})
    assert resp.status_code == 401, (
        f"{metodo} {path} respondio {resp.status_code} sin token. "
        f"Le falta un guard (require_authenticated / require_tutor_or_coordinator / "
        f"require_coordinator) o va agregado a PUBLICOS."
    )


def test_la_matriz_cubre_todos_los_endpoints():
    """Un endpoint nuevo obliga a declarar sus permisos en tests/test_permissions.py."""
    en_matriz = {(m, _concreta(url)) for m, url, _roles in MATRIZ}
    en_app = {(m, _concreta(p)) for m, p in TODOS_LOS_ENDPOINTS}
    faltantes = sorted(en_app - en_matriz - {(m, _concreta(p)) for m, p in PUBLICOS})

    assert not faltantes, (
        "Estos endpoints no estan en la MATRIZ de tests/test_permissions.py:\n  "
        + "\n  ".join(f"{m} {u}" for m, u in faltantes)
        + "\nAgregalos con los roles que corresponda."
    )