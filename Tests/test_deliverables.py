from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.models.deliverable import Deliverable
from app.core.repositories.deliverable_repository import DeliverableRepository
from app.core.schemas.deliverable import DeliverableUpdate
from app.core.services.deliverable_service import DeliverableService
from sqlalchemy import text


def make_deliverable(id=1, group_id=4, stage_id=2, stage_name="Modelo de Negocio", expected_date=date(2026, 4, 20), status="Pending"):
    deliverable = MagicMock(id=id, group_id=group_id, stage_id=stage_id, expected_date=expected_date, status=status)
    deliverable.stage.name = stage_name
    return deliverable


@pytest.fixture
def service():
    svc = DeliverableService(db=MagicMock())
    svc.repository = MagicMock()
    return svc


# =====================================================================
# Service 

# ---- Listado ----

def test_get_all_returns_mapped_deliverables(service):
    service.repository.get_all.return_value = [make_deliverable(id=1), make_deliverable(id=2)]

    result = service.get_all(group_id=4)

    assert len(result) == 2
    assert result[0].id == 1
    service.repository.get_all.assert_called_once_with(
        group_id=4, stage_id=None, status=None, page=1, page_size=10
    )


def test_get_all_empty_list(service):
    service.repository.get_all.return_value = []

    result = service.get_all()

    assert result == []


# ---- Obtener entregable ----

def test_get_by_id_success(service):
    service.repository.get_by_id.return_value = make_deliverable(id=5)

    result = service.get_by_id(5)

    assert result.id == 5


def test_get_by_id_not_found_raises_404(service):
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_by_id(999)

    assert exc_info.value.status_code == 404


# ---- Actualizar ----

def test_update_success(service):
    existing = make_deliverable(id=1, status="Pending")
    updated = make_deliverable(id=1, status="Approved")
    service.repository.get_by_id.return_value = existing
    service.repository.update.return_value = updated

    result = service.update(DeliverableUpdate(id=1, status="Approved"))

    assert result.status == "Approved"
    service.repository.update.assert_called_once_with(existing, {"status": "Approved"})


def test_update_not_found_raises_404(service):
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.update(DeliverableUpdate(id=999, status="Approved"))

    assert exc_info.value.status_code == 404
    service.repository.update.assert_not_called()


def test_update_invalid_status_raises_400(service):
    service.repository.get_by_id.return_value = make_deliverable(id=1)

    with pytest.raises(HTTPException) as exc_info:
        service.update(DeliverableUpdate(id=1, status="Aprobado"))  # no está en VALID_STATUSES

    assert exc_info.value.status_code == 400
    service.repository.update.assert_not_called()


# ---- Pendientes ----

def test_get_pending_filters_by_status(service):
    service.repository.get_by_status.return_value = [make_deliverable(status="Pending")]

    result = service.get_pending()

    assert len(result) == 1
    service.repository.get_by_status.assert_called_once_with("Pending")


# ---- Vencidos ----

def test_get_overdue_uses_today(service):
    service.repository.get_overdue.return_value = [make_deliverable()]

    with patch("app.core.services.deliverable_service.date") as mock_date:
        mock_date.today.return_value = date(2026, 7, 28)
        result = service.get_overdue()

    service.repository.get_overdue.assert_called_once_with(date(2026, 7, 28))
    assert len(result) == 1


# =====================================================================
# Repository 

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Deliverable.__table__.create(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE stages (
                    id INTEGER PRIMARY KEY,
                    cohort_id INTEGER NOT NULL,
                    name VARCHAR(120) NOT NULL,
                    "order" INTEGER NOT NULL,
                    key_dates TEXT
                )
                """
            )
        )
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture
def repo(db):
    return DeliverableRepository(db)


def add_deliverable(db, id, group_id, stage_id, status, expected_date=date(2026, 4, 20)):
    deliverable = Deliverable(
        id=id, group_id=group_id, stage_id=stage_id, status=status, expected_date=expected_date
    )
    db.add(deliverable)
    db.commit()
    return deliverable


# ---- get_all: filtros ----

def test_get_all_no_filters_returns_everything(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending")
    add_deliverable(db, 2, group_id=5, stage_id=2, status="Approved")

    result = repo.get_all()

    assert len(result) == 2


def test_get_all_filters_by_group_id(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending")
    add_deliverable(db, 2, group_id=5, stage_id=2, status="Approved")

    result = repo.get_all(group_id=4)

    assert len(result) == 1
    assert result[0].group_id == 4


def test_get_all_filters_by_stage_id(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending")
    add_deliverable(db, 2, group_id=4, stage_id=2, status="Pending")

    result = repo.get_all(stage_id=2)

    assert len(result) == 1
    assert result[0].stage_id == 2


def test_get_all_filters_by_status(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending")
    add_deliverable(db, 2, group_id=4, stage_id=1, status="Approved")

    result = repo.get_all(status="Approved")

    assert len(result) == 1
    assert result[0].status == "Approved"


def test_get_all_combines_filters(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending")
    add_deliverable(db, 2, group_id=4, stage_id=1, status="Approved")
    add_deliverable(db, 3, group_id=5, stage_id=1, status="Approved")

    result = repo.get_all(group_id=4, status="Approved")

    assert len(result) == 1
    assert result[0].id == 2


def test_get_all_respects_pagination(db, repo):
    for i in range(1, 6):
        add_deliverable(db, i, group_id=4, stage_id=1, status="Pending")

    page_1 = repo.get_all(page=1, page_size=2)
    page_2 = repo.get_all(page=2, page_size=2)

    assert [d.id for d in page_1] == [1, 2]
    assert [d.id for d in page_2] == [3, 4]


# ---- get_by_id ----

def test_get_by_id_found(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending")

    result = repo.get_by_id(1)

    assert result is not None
    assert result.id == 1


def test_get_by_id_not_found(db, repo):
    result = repo.get_by_id(999)

    assert result is None


# ---- get_overdue ----

def test_get_overdue_excludes_done_statuses(db, repo):
    add_deliverable(db, 1, group_id=4, stage_id=1, status="Pending", expected_date=date(2020, 1, 1))
    add_deliverable(db, 2, group_id=4, stage_id=1, status="Approved", expected_date=date(2020, 1, 1))
    add_deliverable(db, 3, group_id=4, stage_id=1, status="Pending", expected_date=date(2099, 1, 1))

    result = repo.get_overdue(today=date(2026, 7, 28))

    assert [d.id for d in result] == [1]
    