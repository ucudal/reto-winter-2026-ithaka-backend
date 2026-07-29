from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.schemas.student import StudentUpsert
from app.core.services.student_service import StudentService


def make_student(id=1, name="Ana Fernández", email="ana@correo.uy", group_id=None,
                  major=None, is_graduation_project=False, linkedin_url=None):
    student = MagicMock()
    student.id = id
    student.name = name
    student.email = email
    student.group_id = group_id
    student.major = major
    student.is_graduation_project = is_graduation_project
    student.linkedin_url = linkedin_url
    return student


@pytest.fixture
def service():
    svc = StudentService(db=MagicMock())
    svc.repo = MagicMock()
    return svc


# ---- Listado ----

def test_list_students_returns_students(service):
    service.repo.get_all.return_value = [make_student(id=1), make_student(id=2)]

    result = service.list_students(page=2, page_size=5)

    assert len(result) == 2
    assert result[0].id == 1
    service.repo.get_all.assert_called_once_with(group_id=None, search=None, page=2, page_size=5)


def test_list_students_empty_list(service):
    service.repo.get_all.return_value = []

    result = service.list_students()

    assert result == []
    service.repo.get_all.assert_called_once_with(group_id=None, search=None, page=1, page_size=10)


def test_list_students_filters_by_group_id(service):
    service.repo.get_all.return_value = [make_student(id=1, group_id=4)]

    result = service.list_students(group_id=4)

    assert len(result) == 1
    service.repo.get_all.assert_called_once_with(group_id=4, search=None, page=1, page_size=10)


def test_list_students_filters_by_search(service):
    service.repo.get_all.return_value = [make_student(id=1, name="Ana Fernández")]

    result = service.list_students(search="Ana")

    assert len(result) == 1
    service.repo.get_all.assert_called_once_with(group_id=None, search="Ana", page=1, page_size=10)


# ---- Obtener estudiante ----

def test_get_student_success(service):
    service.repo.get_by_id.return_value = make_student(id=5)

    result = service.get_student(5)

    assert result.id == 5


def test_get_student_not_found_raises_404(service):
    service.repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_student(999)

    assert exc_info.value.status_code == 404


# ---- Actualizar / Crear (upsert) ----

def test_upsert_creates_when_id_is_none(service):
    service.db.get.return_value = None  # group_id es None, no valida
    created = make_student(id=10, name="Luca Rossi")
    service.repo.create.return_value = created

    payload = StudentUpsert(name="Luca Rossi", email="luca@correo.uy", group_id=None)
    result = service.upsert_student(payload)

    assert result.id == 10
    service.repo.create.assert_called_once_with(payload)
    service.repo.update.assert_not_called()


def test_upsert_updates_when_id_given(service):
    existing = make_student(id=1, name="Ana Vieja")
    updated = make_student(id=1, name="Ana Nueva")
    service.db.get.return_value = None  # group_id es None, no valida
    service.repo.get_by_id.return_value = existing
    service.repo.update.return_value = updated

    payload = StudentUpsert(id=1, name="Ana Nueva", email="ana@correo.uy", group_id=None)
    result = service.upsert_student(payload)

    assert result.name == "Ana Nueva"
    service.repo.update.assert_called_once_with(existing, payload)
    service.repo.create.assert_not_called()


def test_upsert_not_found_raises_404(service):
    service.db.get.return_value = None  # group_id es None, no valida
    service.repo.get_by_id.return_value = None

    payload = StudentUpsert(id=999, name="Fantasma", email="fantasma@correo.uy", group_id=None)

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_student(payload)

    assert exc_info.value.status_code == 404
    service.repo.update.assert_not_called()


# ---- Eliminar ----

def test_delete_student_success(service):
    student = make_student(id=1)
    service.repo.get_by_id.return_value = student

    service.delete_student(1)

    service.repo.delete.assert_called_once_with(student)


def test_delete_student_not_found_raises_404(service):
    service.repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.delete_student(999)

    assert exc_info.value.status_code == 404
    service.repo.delete.assert_not_called()


# ---- Validaciones ----

def test_upsert_raises_400_when_group_does_not_exist(service):
    service.db.get.return_value = None  # simula que el Group con ese id no existe

    payload = StudentUpsert(name="Mateo Silva", email="mateo@correo.uy", group_id=42)

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_student(payload)

    assert exc_info.value.status_code == 400
    service.repo.create.assert_not_called()


def test_upsert_does_not_check_group_when_group_id_is_none(service):
    payload = StudentUpsert(name="Mateo Silva", email="mateo@correo.uy", group_id=None)
    service.repo.create.return_value = make_student(name="Mateo Silva")

    service.upsert_student(payload)

    service.db.get.assert_not_called()


def test_upsert_creates_when_group_exists(service):
    service.db.get.return_value = object()  # simula que el Group sí existe
    created = make_student(name="Camila Torres")
    service.repo.create.return_value = created

    payload = StudentUpsert(name="Camila Torres", email="camila@correo.uy", group_id=7)
    result = service.upsert_student(payload)

    assert result.name == "Camila Torres"
    service.repo.create.assert_called_once_with(payload)