from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.models.enums import TutorRole
from app.core.schemas.tutor import TutorUpsertRequest
from app.core.services.tutor_service import TutorService


def make_service():
    mock_repo = MagicMock()
    service = TutorService(repository=mock_repo)
    return service, mock_repo


def make_tutor(id=1, max_capacity=10, role=TutorRole.TECHNICAL, name="Tutor Test", status="Active"):
    # SimpleNamespace en vez de MagicMock: "name" es un kwarg reservado del
    # constructor de Mock/MagicMock (controla su repr interno), asi que
    # MagicMock(name="Tutor Test") NO asigna el atributo .name como uno
    # esperaria -- devuelve otro MagicMock al leerlo. SimpleNamespace no
    # tiene ese problema, es un simple contenedor de atributos.
    return SimpleNamespace(
        id=id,
        name=name,
        role=role,
        specialty=None,
        max_capacity=max_capacity,
        availability=None,
        status=status,
        linkedin_url=None,
    )


# ---------- listado ----------

def test_list_tutors_devuelve_listado(mock_db):
    service, mock_repo = make_service()
    mock_repo.list.return_value = [make_tutor(id=1), make_tutor(id=2)]

    result = service.list_tutors(mock_db)

    assert len(result) == 2
    mock_repo.list.assert_called_once_with(
        mock_db, role=None, status=None, search=None, page=1, page_size=10
    )


def test_list_tutors_filtra_por_rol_y_busqueda(mock_db):
    service, mock_repo = make_service()
    mock_repo.list.return_value = [make_tutor(id=1)]

    service.list_tutors(mock_db, role=TutorRole.BUSINESS, search="Ana")

    mock_repo.list.assert_called_once_with(
        mock_db, role=TutorRole.BUSINESS, status=None, search="Ana", page=1, page_size=10
    )


# ---------- obtener tutor ----------

def test_get_tutor_exitoso(mock_db):
    service, mock_repo = make_service()
    tutor = make_tutor(id=1)
    mock_repo.get_by_id.return_value = tutor

    result = service.get_tutor(mock_db, 1)

    assert result == tutor


def test_get_tutor_inexistente_tira_404(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_tutor(mock_db, 999)

    assert exc_info.value.status_code == 404


# ---------- actualizar ----------
# Ojo: TutorService.upsert_tutor SIEMPRE termina llamando a repo.update
# (tanto en el flujo de creacion como en el de edicion), asi que en ambos
# casos hay que mockear el return_value de "update", no solo el de "create".

def test_upsert_tutor_crea_nuevo_cuando_no_hay_id(mock_db):
    service, mock_repo = make_service()
    creado = make_tutor(id=10)
    actualizado = make_tutor(id=10, name="Nuevo Tutor")
    mock_repo.create.return_value = creado
    mock_repo.update.return_value = actualizado

    payload = TutorUpsertRequest(name="Nuevo Tutor", role=TutorRole.TECHNICAL, max_capacity=8)
    result = service.upsert_tutor(mock_db, payload)

    mock_repo.create.assert_called_once_with(mock_db, payload)
    mock_repo.update.assert_called_once_with(mock_db, creado, payload)
    assert result.id == 10
    assert result.name == "Nuevo Tutor"


def test_upsert_tutor_actualiza_existente(mock_db):
    service, mock_repo = make_service()
    existente = make_tutor(id=5)
    actualizado = make_tutor(id=5, name="Tutor Actualizado")
    mock_repo.get_by_id.return_value = existente
    mock_repo.update.return_value = actualizado

    payload = TutorUpsertRequest(id=5, name="Tutor Actualizado", role=TutorRole.BUSINESS, max_capacity=12)
    result = service.upsert_tutor(mock_db, payload)

    mock_repo.get_by_id.assert_called_once_with(mock_db, 5)
    mock_repo.update.assert_called_once_with(mock_db, existente, payload)
    mock_repo.create.assert_not_called()
    assert result.id == 5
    assert result.name == "Tutor Actualizado"


def test_upsert_tutor_id_inexistente_tira_404(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = None

    payload = TutorUpsertRequest(id=999, name="Fantasma", role=TutorRole.BUSINESS, max_capacity=10)

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_tutor(mock_db, payload)

    assert exc_info.value.status_code == 404
    mock_repo.update.assert_not_called()


# ---------- obtener grupos ----------

def test_get_tutor_groups_exitoso(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = make_tutor(id=1)
    mock_repo.list_groups.return_value = [MagicMock(id=1), MagicMock(id=2)]

    result = service.get_tutor_groups(mock_db, 1)

    assert len(result) == 2
    mock_repo.list_groups.assert_called_once_with(mock_db, 1)


def test_get_tutor_groups_tutor_inexistente_tira_404(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_tutor_groups(mock_db, 999)

    assert exc_info.value.status_code == 404
    mock_repo.list_groups.assert_not_called()


# ---------- calcular capacidad ----------

def test_get_tutor_capacity_calcula_correctamente(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = make_tutor(id=1, max_capacity=10)
    mock_repo.list_meetings.return_value = [
        SimpleNamespace(hours_spent=3),
        SimpleNamespace(hours_spent=2),
    ]

    result = service.get_tutor_capacity(mock_db, 1)

    assert result["assigned_hours"] == 5
    assert result["available_hours"] == 5
    assert result["usage_percentage"] == 50.0
    assert result["overloaded"] is False


def test_get_tutor_capacity_con_max_capacity_cero_no_rompe(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = make_tutor(id=1, max_capacity=0)
    mock_repo.list_meetings.return_value = []

    result = service.get_tutor_capacity(mock_db, 1)

    assert result["usage_percentage"] == 0
    assert result["overloaded"] is False


def test_get_tutor_capacity_sin_reuniones_devuelve_cero_horas(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = make_tutor(id=1, max_capacity=10)
    mock_repo.list_meetings.return_value = []

    result = service.get_tutor_capacity(mock_db, 1)

    assert result["assigned_hours"] == 0
    assert result["available_hours"] == 10


# ---------- tutor sobrecargado ----------

def test_list_overloaded_incluye_solo_tutores_sobrecargados(mock_db):
    service, mock_repo = make_service()
    tutor_ok = make_tutor(id=1, max_capacity=10)
    tutor_sobrecargado = make_tutor(id=2, max_capacity=5)
    mock_repo.list_all.return_value = [tutor_ok, tutor_sobrecargado]

    def list_meetings_side_effect(db, tutor_id):
        return [SimpleNamespace(hours_spent=3)] if tutor_id == 1 else [SimpleNamespace(hours_spent=8)]

    mock_repo.list_meetings.side_effect = list_meetings_side_effect

    result = service.list_overloaded(mock_db)

    assert len(result) == 1
    assert result[0]["tutor_id"] == 2
    assert result[0]["overloaded"] is True


def test_list_overloaded_sin_tutores_sobrecargados_devuelve_vacio(mock_db):
    service, mock_repo = make_service()
    mock_repo.list_all.return_value = [make_tutor(id=1, max_capacity=10)]
    mock_repo.list_meetings.return_value = [SimpleNamespace(hours_spent=2)]

    result = service.list_overloaded(mock_db)

    assert result == []


# ---------- validaciones ----------

def test_tutor_upsert_requiere_name():
    with pytest.raises(ValidationError):
        TutorUpsertRequest(role=TutorRole.TECHNICAL, max_capacity=10)


def test_tutor_upsert_rechaza_rol_invalido():
    with pytest.raises(ValidationError):
        TutorUpsertRequest(name="Tutor", role="NoExiste", max_capacity=10)


def test_tutor_upsert_max_capacity_debe_ser_numerico():
    with pytest.raises(ValidationError):
        TutorUpsertRequest(name="Tutor", role=TutorRole.TECHNICAL, max_capacity="mucho")
