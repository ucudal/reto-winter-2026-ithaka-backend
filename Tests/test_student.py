from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.models.student import Student
from app.core.repositories.student_repository import StudentRepository
from app.core.schemas.student import StudentUpsert
from app.core.services.student_service import StudentService


# ======================================================================
# Helpers

def make_student(id=1, name="Ana Fernández", email="ana@correo.uy", group_id=None,
                  major=None, is_graduation_project=False, linkedin_url=None):
    """Crea un MagicMock que simula un Student, para los tests del service."""
    student = MagicMock()
    student.id = id
    student.name = name
    student.email = email
    student.group_id = group_id
    student.major = major
    student.is_graduation_project = is_graduation_project
    student.linkedin_url = linkedin_url
    return student


# ======================================================================
# Tests del SERVICE (con repo y db mockeados)

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
    service.db.get.return_value = None 
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
    service.db.get.return_value = None
    service.repo.get_by_id.return_value = existing
    service.repo.update.return_value = updated

    payload = StudentUpsert(id=1, name="Ana Nueva", email="ana@correo.uy", group_id=None)
    result = service.upsert_student(payload)

    assert result.name == "Ana Nueva"
    service.repo.update.assert_called_once_with(existing, payload)
    service.repo.create.assert_not_called()


def test_upsert_not_found_raises_404(service):
    service.db.get.return_value = None
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
    service.db.get.return_value = None

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
    service.db.get.return_value = object()
    created = make_student(name="Camila Torres")
    service.repo.create.return_value = created

    payload = StudentUpsert(name="Camila Torres", email="camila@correo.uy", group_id=7)
    result = service.upsert_student(payload)

    assert result.name == "Camila Torres"
    service.repo.create.assert_called_once_with(payload)


# ======================================================================
# Tests del REPOSITORY (contra SQLite en memoria, sin mocks)

@pytest.fixture()
def db_session():
    """Sesión contra una base SQLite en memoria, con solo la tabla students creada.

    No usamos Base.metadata.create_all() porque intentaría crear TODAS las
    tablas registradas en Base (incluidas stages, meetings, etc.), y algunas
    de ellas usan columnas JSONB (el tipo específico de Postgres), que SQLite
    no sabe compilar. Como Student no tiene columnas JSONB y SQLite no valida
    foreign keys por defecto, alcanza con crear solo su tabla.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Student.__table__.create(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def repository(db_session):
    return StudentRepository(db_session)


def _make_student_row(db_session, name="Ana Fernández", email="ana@correo.uy", group_id=None) -> Student:
    student = Student(name=name, email=email, group_id=group_id, is_graduation_project=False)
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


# ---- Listado ----

def test_repo_get_all_returns_empty_list_when_no_students(repository):
    assert repository.get_all() == []


def test_repo_get_all_returns_all_students_within_page(db_session, repository):
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy")
    _make_student_row(db_session, "Luca Rossi", "luca@correo.uy")
    _make_student_row(db_session, "Mateo Silva", "mateo@correo.uy")

    result = repository.get_all(page=1, page_size=10)

    assert len(result) == 3


def test_repo_get_all_respects_pagination(db_session, repository):
    for i in range(5):
        _make_student_row(db_session, f"Estudiante {i}", f"estudiante{i}@correo.uy")

    page_1 = repository.get_all(page=1, page_size=2)
    page_2 = repository.get_all(page=2, page_size=2)
    page_3 = repository.get_all(page=3, page_size=2)

    assert len(page_1) == 2
    assert len(page_2) == 2
    assert len(page_3) == 1
    assert {s.id for s in page_1}.isdisjoint({s.id for s in page_2})


def test_repo_get_all_orders_results_by_name_then_id(db_session, repository):
    _make_student_row(db_session, "Zulema Paz", "zulema@correo.uy")
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy")
    _make_student_row(db_session, "Mateo Silva", "mateo@correo.uy")

    result = repository.get_all(page=1, page_size=10)

    assert [s.name for s in result] == ["Ana Fernández", "Mateo Silva", "Zulema Paz"]


def test_repo_get_all_filters_by_group_id(db_session, repository):
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy", group_id=1)
    _make_student_row(db_session, "Luca Rossi", "luca@correo.uy", group_id=1)
    _make_student_row(db_session, "Mateo Silva", "mateo@correo.uy", group_id=2)

    result = repository.get_all(group_id=1)

    assert len(result) == 2
    assert all(s.group_id == 1 for s in result)


def test_repo_get_all_filters_by_group_id_returns_empty_when_no_match(db_session, repository):
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy", group_id=1)

    assert repository.get_all(group_id=999) == []


def test_repo_get_all_filters_by_search_case_insensitive_partial_match(db_session, repository):
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy")
    _make_student_row(db_session, "Luca Rossi", "luca@correo.uy")

    result = repository.get_all(search="fern")

    assert len(result) == 1
    assert result[0].name == "Ana Fernández"


def test_repo_get_all_filters_by_search_returns_empty_when_no_match(db_session, repository):
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy")

    assert repository.get_all(search="xyz-no-existe") == []


def test_repo_get_all_combines_group_id_and_search_filters(db_session, repository):
    _make_student_row(db_session, "Ana Fernández", "ana@correo.uy", group_id=1)
    _make_student_row(db_session, "Ana Torres", "ana.torres@correo.uy", group_id=2)

    result = repository.get_all(group_id=1, search="Ana")

    assert len(result) == 1
    assert result[0].email == "ana@correo.uy"


# ---- Obtener estudiante ----

def test_repo_get_by_id_returns_student_when_exists(db_session, repository):
    created = _make_student_row(db_session)

    found = repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.name == "Ana Fernández"


def test_repo_get_by_id_returns_none_when_not_exists(repository):
    assert repository.get_by_id(9999) is None


# ---- Crear ----

def test_repo_create_persists_student_with_given_data(repository):
    payload = StudentUpsert(
        name="Camila Torres",
        email="camila@correo.uy",
        major="Ingeniería Biomédica",
        group_id=None,
        is_graduation_project=True,
        linkedin_url=None,
    )

    created = repository.create(payload)

    assert created.id is not None
    assert created.name == "Camila Torres"
    assert created.email == "camila@correo.uy"
    assert created.is_graduation_project is True


def test_repo_created_student_is_retrievable(repository):
    payload = StudentUpsert(name="Joaquín Olivera", email="joaquin@correo.uy")

    created = repository.create(payload)
    fetched = repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.email == "joaquin@correo.uy"


# ---- Actualizar ----

def test_repo_update_updates_fields_and_persists_changes(db_session, repository):
    student = _make_student_row(db_session)
    payload = StudentUpsert(
        id=student.id,
        name="Ana Fernández (actualizada)",
        email="ana@correo.uy",
        major="Ingeniería en Informática",
        group_id=None,
        is_graduation_project=True,
        linkedin_url="https://www.linkedin.com/in/ana-fernandez",
    )

    updated = repository.update(student, payload)

    assert updated.name == "Ana Fernández (actualizada)"
    assert updated.major == "Ingeniería en Informática"
    assert updated.is_graduation_project is True
    assert updated.linkedin_url == "https://www.linkedin.com/in/ana-fernandez"


def test_repo_update_is_persisted_to_db(db_session, repository):
    student = _make_student_row(db_session)
    payload = StudentUpsert(id=student.id, name="Nombre Nuevo", email=student.email)

    repository.update(student, payload)
    fetched = repository.get_by_id(student.id)

    assert fetched.name == "Nombre Nuevo"


# ---- Eliminar ----

def test_repo_delete_removes_student_from_db(db_session, repository):
    student = _make_student_row(db_session)

    repository.delete(student)

    assert repository.get_by_id(student.id) is None