from __future__ import annotations
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.repositories.group_repository import GroupRepository
from app.core.services.group_service import GroupService

MOD = "app.core.services.group_service"


@pytest.fixture()
def mock_repository():
    return MagicMock(spec=GroupRepository)


@pytest.fixture()
def service(mock_repository):
    s = GroupService(repository=mock_repository)
    s.cohort_repository = MagicMock()
    return s


def test_get_group_returns_group_when_found(service, mock_repository, monkeypatch):
    mock_repository.get_by_id.return_value = MagicMock()
    monkeypatch.setattr(f"{MOD}.user_can_access_group", lambda group, user: True)
    fake_response = MagicMock()
    fake_response.model_validate.return_value = "GROUP_RESPONSE"
    monkeypatch.setattr(f"{MOD}.GroupResponse", fake_response)

    result = service.get_group(db=MagicMock(), group_id=5, current_user=MagicMock())

    assert result == "GROUP_RESPONSE"


def test_get_group_raises_404_when_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_group(db=MagicMock(), group_id=999, current_user=MagicMock())

    assert exc_info.value.status_code == 404


def test_get_group_raises_403_when_no_access(service, mock_repository, monkeypatch):
    mock_repository.get_by_id.return_value = MagicMock()
    monkeypatch.setattr(f"{MOD}.user_can_access_group", lambda group, user: False)

    with pytest.raises(HTTPException) as exc_info:
        service.get_group(db=MagicMock(), group_id=5, current_user=MagicMock())

    assert exc_info.value.status_code == 403


def test_delete_group_calls_repository(service, mock_repository):
    group = MagicMock()
    mock_repository.get_by_id.return_value = group

    service.delete_group(db=MagicMock(), group_id=5)

    mock_repository.delete.assert_called_once()


def test_delete_group_raises_404_when_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.delete_group(db=MagicMock(), group_id=999)

    assert exc_info.value.status_code == 404


def test_upsert_group_rejects_empty_students(service):
    service.cohort_repository.get_by_id.return_value = MagicMock()  # cohort existe

    payload = MagicMock(id=None, cohort_id=1, student_ids=[])

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_group(db=MagicMock(), payload=payload)

    assert exc_info.value.status_code == 400