from __future__ import annotations
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.models.cohort import Cohort
from app.core.repositories.cohort_repository import CohortRepository
from app.core.schemas.cohort import CohortUpsertRequest
from app.core.services.cohort_service import CohortService


def _make_cohort(cohort_id: int = 1, **overrides) -> Cohort:
    defaults = {
        "id": cohort_id,
        "year": 2026,
        "semester": 1,
        "start_date": date(2026, 3, 1),
        "end_date": None,
        "status": "Active",
        "notes": None,
    }
    defaults.update(overrides)
    return Cohort(**defaults)


@pytest.fixture()
def mock_repository():
    return MagicMock(spec=CohortRepository)


@pytest.fixture()
def service(mock_repository):
    return CohortService(repository=mock_repository)


def test_list_cohorts_returns_read_models(service, mock_repository):
    mock_repository.list.return_value = [_make_cohort(1), _make_cohort(2)]
    mock_repository.count_groups.return_value = 3

    result = service.list_cohorts(db=MagicMock())

    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].group_count == 3


def test_get_cohort_returns_cohort_when_found(service, mock_repository):
    mock_repository.get_by_id.return_value = _make_cohort(5)
    mock_repository.count_groups.return_value = 0

    result = service.get_cohort(db=MagicMock(), cohort_id=5)

    assert result.id == 5
    assert result.year == 2026


def test_get_cohort_raises_404_when_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_cohort(db=MagicMock(), cohort_id=999)

    assert exc_info.value.status_code == 404


def test_upsert_cohort_updates_existing_cohort(service, mock_repository):
    existing = _make_cohort(1, year=2025)
    updated = _make_cohort(1, year=2026)
    mock_repository.get_by_id.return_value = existing
    mock_repository.update.return_value = updated
    mock_repository.count_groups.return_value = 0

    payload = CohortUpsertRequest(
        id=1, year=2026, semester=1, start_date=date(2026, 3, 1)
    )
    result = service.upsert_cohort(db=MagicMock(), payload=payload)

    assert result.year == 2026
    mock_repository.update.assert_called_once()


def test_upsert_cohort_rejects_invalid_semester(service, mock_repository):
    payload = CohortUpsertRequest(
        id=1, year=2026, semester=3, start_date=date(2026, 3, 1)
    )

    with pytest.raises(HTTPException) as exc_info:
        service.upsert_cohort(db=MagicMock(), payload=payload)

    assert exc_info.value.status_code == 400