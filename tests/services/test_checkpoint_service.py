from __future__ import annotations
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.models.checkpoint import Checkpoint
from app.core.repositories.checkpoint_repository import CheckpointRepository
from app.core.schemas.checkpoint import CheckpointUpdateRequest
from app.core.services.checkpoint_service import CheckpointService


def _make_checkpoint(checkpoint_id: int = 1, **overrides) -> Checkpoint:
    defaults = {
        "id": checkpoint_id,
        "group_id": 1,
        "cohort_id": 1,
        "title": "Checkpoint de prueba",
        "due_date": date(2026, 6, 1),
        "status": "Pending",
        "questions": [],
    }
    defaults.update(overrides)
    return Checkpoint(**defaults)


@pytest.fixture()
def mock_repository():
    return MagicMock(spec=CheckpointRepository)


@pytest.fixture()
def service(mock_repository):
    return CheckpointService(repository=mock_repository)


def test_list_checkpoints_returns_read_models(service, mock_repository):
    mock_repository.list.return_value = [_make_checkpoint(1), _make_checkpoint(2)]

    result = service.list_checkpoints(db=MagicMock())

    assert len(result) == 2
    assert result[0].id == 1


def test_get_checkpoint_returns_checkpoint_when_found(service, mock_repository):
    mock_repository.get_by_id.return_value = _make_checkpoint(5)

    result = service.get_checkpoint(db=MagicMock(), checkpoint_id=5)

    assert result.id == 5


def test_get_checkpoint_raises_404_when_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_checkpoint(db=MagicMock(), checkpoint_id=999)

    assert exc_info.value.status_code == 404


def test_update_checkpoint_raises_404_when_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None
    payload = CheckpointUpdateRequest(status="Closed")

    with pytest.raises(HTTPException) as exc_info:
        service.update_checkpoint(db=MagicMock(), checkpoint_id=999, payload=payload)

    assert exc_info.value.status_code == 404


def test_update_checkpoint_updates_existing_checkpoint(service, mock_repository):
    existing = _make_checkpoint(1, status="Pending")
    updated = _make_checkpoint(1, status="Closed")
    mock_repository.get_by_id.return_value = existing
    mock_repository.update.return_value = updated

    payload = CheckpointUpdateRequest(status="Closed")
    result = service.update_checkpoint(db=MagicMock(), checkpoint_id=1, payload=payload)

    assert result.status == "Closed"
    mock_repository.update.assert_called_once()


def test_my_pending_includes_checkpoint_within_reminder_window(service, mock_repository):
    # due_date es hoy + 5 días -> ya entró en la ventana de 10 días de aviso
    checkpoint = _make_checkpoint(1, due_date=date.today() + __import__("datetime").timedelta(days=5))
    mock_repository.list.return_value = [checkpoint]

    result = service.my_pending(db=MagicMock(), user=MagicMock())

    assert len(result) == 1


def test_my_pending_excludes_checkpoint_outside_reminder_window(service, mock_repository):
    # due_date es hoy + 20 días -> todavía no entró en la ventana de aviso
    checkpoint = _make_checkpoint(1, due_date=date.today() + __import__("datetime").timedelta(days=20))
    mock_repository.list.return_value = [checkpoint]

    result = service.my_pending(db=MagicMock(), user=MagicMock())

    assert len(result) == 0