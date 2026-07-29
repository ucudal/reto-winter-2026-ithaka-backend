"""Matriz de permisos: valida que cada endpoint acepte exactamente los roles esperados.

Si alguien cambia un guard sin querer, estos tests lo cazan.
"""
from __future__ import annotations

import pytest

TODOS = ("coordinator", "business_tutor", "technical_tutor", "student")
TUTORES = ("coordinator", "business_tutor", "technical_tutor")
SOLO_COORD = ("coordinator",)

# (metodo, url, roles permitidos)
MATRIZ = [
    # Users
    ("GET", "/api/users/me", TODOS),
    ("GET", "/api/users", SOLO_COORD),
    ("POST", "/api/users", SOLO_COORD),
    ("PUT", "/api/users/1", SOLO_COORD),
    ("DELETE", "/api/users/1", SOLO_COORD),
    # Cohorts
    ("GET", "/api/cohorts", TODOS),
    ("GET", "/api/cohorts/1", TODOS),
    ("GET", "/api/cohorts/1/groups", TODOS),
    ("GET", "/api/cohorts/1/stages", TODOS),
    ("PUT", "/api/cohorts", SOLO_COORD),
    # Groups
    ("GET", "/api/groups", TODOS),
    ("GET", "/api/groups/1", TODOS),
    ("GET", "/api/groups/1/students", TODOS),
    ("GET", "/api/groups/1/meetings", TODOS),
    ("GET", "/api/groups/1/deliverables", TODOS),
    ("GET", "/api/groups/1/documents", TODOS),
    ("PATCH", "/api/groups/1/stage", TUTORES),
    ("PUT", "/api/groups/1/documents", TUTORES),
    ("PUT", "/api/groups", SOLO_COORD),
    ("DELETE", "/api/groups/1", SOLO_COORD),
    ("PATCH", "/api/groups/1/tutors", SOLO_COORD),
    # Students
    ("GET", "/api/students", TUTORES),
    ("GET", "/api/students/1", TODOS),
    ("PUT", "/api/students", SOLO_COORD),
    ("DELETE", "/api/students/1", SOLO_COORD),
    # Tutors
    ("GET", "/api/tutors", TODOS),
    ("GET", "/api/tutors/1", TODOS),
    ("GET", "/api/tutors/1/groups", TUTORES),
    ("GET", "/api/tutors/1/capacity", TUTORES),
    ("GET", "/api/tutors/overloaded", SOLO_COORD),
    ("PUT", "/api/tutors", SOLO_COORD),
    # Stages
    ("GET", "/api/stages", TODOS),
    ("GET", "/api/stages/1/expected-deliverables", TODOS),
    ("PUT", "/api/stages", SOLO_COORD),
    # Deliverables
    ("GET", "/api/deliverables", TODOS),
    ("GET", "/api/deliverables/1", TODOS),
    ("GET", "/api/deliverables/pending", TUTORES),
    ("GET", "/api/deliverables/overdue", TUTORES),
    ("PUT", "/api/deliverables", TUTORES),
    # Comments
    ("GET", "/api/deliverables/1/comments", TODOS),
    ("PUT", "/api/deliverables/1/comments", TUTORES),
    ("DELETE", "/api/comments/1", TUTORES),
    # Documents
    ("GET", "/api/deliverables/1/documents", TODOS),
    ("PUT", "/api/deliverables/1/documents", TUTORES),
    ("DELETE", "/api/documents/1", SOLO_COORD),
    # Support materials
    ("GET", "/api/materials", TODOS),
    ("GET", "/api/materials/1", TODOS),
    ("PUT", "/api/materials", TUTORES),
    ("DELETE", "/api/materials/1", SOLO_COORD),
    # Meetings
    ("GET", "/api/meetings", TODOS),
    ("GET", "/api/meetings/1", TODOS),
    ("PUT", "/api/meetings", TUTORES),
    ("DELETE", "/api/meetings/1", TUTORES),
    ("GET", "/api/groups/1/meetings/total-hours", TODOS),
    # Checkpoints
    ("GET", "/api/checkpoints", TODOS),
    ("GET", "/api/checkpoints/my-pending", TODOS),
    ("GET", "/api/checkpoints/1", TODOS),
    ("PUT", "/api/checkpoints/1", TUTORES),
    # Dashboard
    ("GET", "/api/dashboard/summary", TUTORES),
]

CASOS = [
    pytest.param(m, url, permitidos, rol, id=f"{m}-{url}-{rol}")
    for m, url, permitidos in MATRIZ
    for rol in TODOS
]


@pytest.mark.parametrize(("metodo", "url", "permitidos", "rol"), CASOS)
def test_rol_permitido_o_prohibido(client, headers, metodo, url, permitidos, rol):
    """403 si el rol no corresponde; cualquier otra cosa si si corresponde.

    No chequeamos 200: la base esta vacia, asi que un 404/422/500 igual prueba
    que el request paso la capa de autorizacion.
    """
    resp = client.request(metodo, url, headers=headers[rol], json={})
    if rol in permitidos:
        assert resp.status_code != 403, f"{rol} deberia poder {metodo} {url}"
        assert resp.status_code != 401, f"{rol} tiene token valido pero dio 401"
    else:
        assert resp.status_code == 403, f"{rol} NO deberia poder {metodo} {url}"


@pytest.mark.parametrize(
    ("metodo", "url"), [(m, url) for m, url, _ in MATRIZ], ids=lambda v: str(v)
)
def test_sin_token_es_401(client, metodo, url):
    assert client.request(metodo, url, json={}).status_code == 401