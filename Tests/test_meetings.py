from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.models.enums import UserRole
from app.core.models.group import Group
from app.core.models.meeting import Meeting, MeetingStatus
from app.core.repositories.meeting_repository import MeetingRepository
from app.core.schemas.meeting import MeetingUpsertRequest
from app.core.services.meeting_service import MeetingService


# =====================================================================
# Helpers

def make_user(id=1, role=UserRole.COORDINATOR):
    return SimpleNamespace(id=id, role=role)


def make_tutor(user_id, max_capacity=0):
    return SimpleNamespace(user_id=user_id, max_capacity=max_capacity)


def make_student(user_id):
    return SimpleNamespace(user_id=user_id)


def make_group(id=1, business_tutor=None, technical_tutor=None, students=None):
    return SimpleNamespace(
        id=id,
        business_tutor=business_tutor,
        technical_tutor=technical_tutor,
        students=students or [],
    )


def make_meeting(
    id=1,
    group=None,
    group_id=1,
    tutor_ids=None,
    status=MeetingStatus.SCHEDULED,
    date_=None,
    participants=None,
    summary=None,
    notes=None,
    next_steps=None,
    hours_spent=None,
    links=None,
):
    meeting = MagicMock(
        id=id,
        group_id=group_id,
        tutor_ids=tutor_ids,
        status=status,
        date=date_ or datetime(2026, 4, 10, 15, 0, tzinfo=timezone.utc),
        participants=participants,
        summary=summary,
        notes=notes,
        next_steps=next_steps,
        hours_spent=hours_spent,
        links=links,
    )
    meeting.group = group
    return meeting


@pytest.fixture
def service():
    return MeetingService(repository=MagicMock())


# =====================================================================
# Service (mockeando el repository)

# ---- Listado ----

def test_list_meetings_filters_by_access(service):
    tutor_user = make_user(id=2, role=UserRole.BUSINESS_TUTOR)

    group_a = make_group(id=1, business_tutor=make_tutor(user_id=2))
    group_b = make_group(id=2, business_tutor=make_tutor(user_id=99))

    meeting_a = make_meeting(id=1, group=group_a, group_id=1)
    meeting_b = make_meeting(id=2, group=group_b, group_id=2)

    service.repository.list.return_value = [meeting_a, meeting_b]

    result = service.list_meetings(db=MagicMock(), current_user=tutor_user)

    assert len(result) == 1
    assert result[0].id == 1


# ---- Obtener reunión ----

def test_get_meeting_success_for_coordinator(service):
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)
    group = make_group(id=1)
    meeting = make_meeting(id=5, group=group)
    service.repository.get_by_id.return_value = meeting

    result = service.get_meeting(db=MagicMock(), meeting_id=5, current_user=coordinator)

    assert result.id == 5


def test_get_meeting_success_for_student_in_group(service):
    student_user = make_user(id=3, role=UserRole.STUDENT)
    group = make_group(id=1, students=[make_student(user_id=3)])
    meeting = make_meeting(id=5, group=group)
    service.repository.get_by_id.return_value = meeting

    result = service.get_meeting(db=MagicMock(), meeting_id=5, current_user=student_user)

    assert result.id == 5


def test_get_meeting_not_found_raises_404(service):
    service.repository.get_by_id.return_value = None
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)

    with pytest.raises(HTTPException) as exc_info:
        service.get_meeting(db=MagicMock(), meeting_id=999, current_user=coordinator)

    assert exc_info.value.status_code == 404


def test_get_meeting_forbidden_for_unrelated_tutor(service):
    unrelated_tutor = make_user(id=2, role=UserRole.BUSINESS_TUTOR)
    group = make_group(id=1, business_tutor=make_tutor(user_id=99))
    meeting = make_meeting(id=5, group=group)
    service.repository.get_by_id.return_value = meeting

    with pytest.raises(HTTPException) as exc_info:
        service.get_meeting(db=MagicMock(), meeting_id=5, current_user=unrelated_tutor)

    assert exc_info.value.status_code == 403


# ---- Actualizar (upsert) ----

def test_upsert_meeting_creates_when_id_is_none(service):
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)
    group = make_group(id=1)
    created = make_meeting(id=10, group=group, group_id=1)
    service.repository.get_group.return_value = group
    service.repository.create.return_value = created

    payload = MeetingUpsertRequest(group_id=1, date=datetime(2026, 8, 5, 15, 0, tzinfo=timezone.utc))

    result = service.upsert_meeting(db=MagicMock(), payload=payload, current_user=coordinator)

    assert result.id == 10
    service.repository.create.assert_called_once()
    service.repository.update.assert_not_called()


def test_upsert_meeting_updates_when_id_is_present(service):
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)
    group = make_group(id=1)
    existing = make_meeting(id=7, group=group, group_id=1)
    updated = make_meeting(id=7, group=group, group_id=1, summary="Actualizado")
    service.repository.get_group.return_value = group
    service.repository.get_by_id.return_value = existing
    service.repository.update.return_value = updated

    payload = MeetingUpsertRequest(id=7, group_id=1, date=datetime(2026, 8, 5, 15, 0, tzinfo=timezone.utc))

    result = service.upsert_meeting(db=MagicMock(), payload=payload, current_user=coordinator)

    assert result.summary == "Actualizado"
    service.repository.update.assert_called_once()
    service.repository.create.assert_not_called()


def test_upsert_meeting_group_not_found_raises_404(service):
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)
    service.repository.get_group.return_value = None

    payload = MeetingUpsertRequest(group_id=999, date=datetime(2026, 8, 5, 15, 0, tzinfo=timezone.utc))

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_meeting(db=MagicMock(), payload=payload, current_user=coordinator)

    assert exc_info.value.status_code == 404


def test_upsert_meeting_forbidden_for_student(service):
    student_user = make_user(id=3, role=UserRole.STUDENT)
    group = make_group(id=1, students=[make_student(user_id=3)])
    service.repository.get_group.return_value = group

    payload = MeetingUpsertRequest(group_id=1, date=datetime(2026, 8, 5, 15, 0, tzinfo=timezone.utc))

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_meeting(db=MagicMock(), payload=payload, current_user=student_user)

    assert exc_info.value.status_code == 403


# ---- Eliminar ----

def test_delete_meeting_success(service):
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)
    group = make_group(id=1)
    meeting = make_meeting(id=5, group=group)
    service.repository.get_by_id.return_value = meeting

    service.delete_meeting(db=MagicMock(), meeting_id=5, current_user=coordinator)

    service.repository.delete.assert_called_once()


def test_delete_meeting_not_found_raises_404(service):
    service.repository.get_by_id.return_value = None
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)

    with pytest.raises(HTTPException) as exc_info:
        service.delete_meeting(db=MagicMock(), meeting_id=999, current_user=coordinator)

    assert exc_info.value.status_code == 404


def test_delete_meeting_forbidden_for_unrelated_tutor(service):
    unrelated_tutor = make_user(id=2, role=UserRole.TECHNICAL_TUTOR)
    group = make_group(id=1, technical_tutor=make_tutor(user_id=99))
    meeting = make_meeting(id=5, group=group)
    service.repository.get_by_id.return_value = meeting

    with pytest.raises(HTTPException) as exc_info:
        service.delete_meeting(db=MagicMock(), meeting_id=5, current_user=unrelated_tutor)

    assert exc_info.value.status_code == 403
    service.repository.delete.assert_not_called()


# ---- Calcular horas del grupo ----

def test_get_group_total_hours_calculates_remaining(service):
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)
    business_tutor = make_tutor(user_id=2, max_capacity=40)
    technical_tutor = make_tutor(user_id=3, max_capacity=20)
    group = make_group(id=1, business_tutor=business_tutor, technical_tutor=technical_tutor)
    service.repository.get_group.return_value = group
    service.repository.sum_hours_by_group.return_value = 15.0

    result = service.get_group_total_hours(db=MagicMock(), group_id=1, current_user=coordinator)

    assert result.total_hours == 15.0
    assert result.max_capacity == 60
    assert result.remaining_hours == 45.0


def test_get_group_total_hours_group_not_found_raises_404(service):
    service.repository.get_group.return_value = None
    coordinator = make_user(id=1, role=UserRole.COORDINATOR)

    with pytest.raises(HTTPException) as exc_info:
        service.get_group_total_hours(db=MagicMock(), group_id=999, current_user=coordinator)

    assert exc_info.value.status_code == 404


def test_get_group_total_hours_forbidden_for_unrelated_tutor(service):
    unrelated_tutor = make_user(id=2, role=UserRole.BUSINESS_TUTOR)
    group = make_group(id=1, business_tutor=make_tutor(user_id=99, max_capacity=40))
    service.repository.get_group.return_value = group

    with pytest.raises(HTTPException) as exc_info:
        service.get_group_total_hours(db=MagicMock(), group_id=1, current_user=unrelated_tutor)

    assert exc_info.value.status_code == 403


# =====================================================================
# Repository (SQLite en memoria)

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Group.__table__.create(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE meetings (
                    id INTEGER PRIMARY KEY,
                    group_id INTEGER NOT NULL,
                    tutor_ids TEXT,
                    status VARCHAR(20) NOT NULL,
                    date DATETIME NOT NULL,
                    participants TEXT,
                    summary TEXT,
                    notes TEXT,
                    next_steps TEXT,
                    hours_spent NUMERIC(5, 2),
                    links TEXT
                )
                """
            )
        )
    session = Session(engine)
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def repo():
    return MeetingRepository()


def add_meeting(db, id, group_id, status=MeetingStatus.SCHEDULED, date_=None, hours_spent=None, tutor_ids=None, participants=None):
    meeting = Meeting(
        id=id,
        group_id=group_id,
        tutor_ids=tutor_ids or [],
        status=status,
        date=date_ or datetime(2026, 4, 10, 15, 0, tzinfo=timezone.utc),
        participants=participants or [],
        hours_spent=hours_spent,
        links=[],
    )
    db.add(meeting)
    db.commit()
    return meeting


def add_group(db, id=1, name="EcoRoute", cohort_id=1):
    group = Group(id=id, name=name, cohort_id=cohort_id)
    db.add(group)
    db.commit()
    return group


# ---- list ----

def test_list_orders_by_date_desc(db, repo):
    add_meeting(db, 1, group_id=1, date_=datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc))
    add_meeting(db, 2, group_id=1, date_=datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc))

    result = repo.list(db)

    assert [m.id for m in result] == [2, 1]


# ---- get_by_id ----

def test_get_by_id_found(db, repo):
    add_meeting(db, 1, group_id=1)

    result = repo.get_by_id(db, 1)

    assert result is not None
    assert result.id == 1


def test_get_by_id_not_found(db, repo):
    result = repo.get_by_id(db, 999)

    assert result is None


# ---- create ----

def test_create_inserts_meeting(db, repo):
    payload = MeetingUpsertRequest(
        group_id=1,
        date=datetime(2026, 8, 5, 15, 0, tzinfo=timezone.utc),
        tutor_ids=[4, 5],
        summary="Nueva reunión",
    )

    created = repo.create(db, payload)

    assert created.id is not None
    assert created.group_id == 1
    assert created.tutor_ids == [4, 5]
    assert created.summary == "Nueva reunión"


# ---- update ----

def test_update_modifies_fields(db, repo):
    meeting = add_meeting(db, 1, group_id=1, status=MeetingStatus.SCHEDULED)
    payload = MeetingUpsertRequest(
        id=1,
        group_id=1,
        date=datetime(2026, 4, 10, 15, 0, tzinfo=timezone.utc),
        status=MeetingStatus.HELD,
        summary="Reunión realizada",
    )

    updated = repo.update(db, meeting, payload)

    assert updated.status == MeetingStatus.HELD
    assert updated.summary == "Reunión realizada"


# ---- delete ----

def test_delete_removes_meeting(db, repo):
    meeting = add_meeting(db, 1, group_id=1)

    repo.delete(db, meeting)

    assert repo.get_by_id(db, 1) is None


# ---- calcular horas del grupo (sum_hours_by_group) ----

def test_sum_hours_by_group_adds_up(db, repo):
    add_meeting(db, 1, group_id=1, hours_spent=2.5)
    add_meeting(db, 2, group_id=1, hours_spent=1.5)
    add_meeting(db, 3, group_id=2, hours_spent=10.0)  # otro grupo, no debería sumar

    result = repo.sum_hours_by_group(db, 1)

    assert result == 4.0


def test_sum_hours_by_group_returns_zero_when_no_meetings(db, repo):
    result = repo.sum_hours_by_group(db, 999)

    assert result == 0


# ---- get_group ----

def test_get_group_found(db, repo):
    add_group(db, id=1, name="EcoRoute")

    result = repo.get_group(db, 1)

    assert result is not None
    assert result.name == "EcoRoute"


def test_get_group_not_found(db, repo):
    result = repo.get_group(db, 999)

    assert result is None