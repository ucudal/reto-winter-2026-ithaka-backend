from __future__ import annotations
from datetime import date

from app.core.repositories.cohort_repository import CohortRepository
from app.core.schemas.cohort import CohortUpsertRequest


def test_list_returns_cohorts_filtered_by_year(db_session, make_cohort):
    target = make_cohort(year=2099, semester=1)  # año poco común, evita chocar con datos del seeder
    other = make_cohort(year=2020, semester=1)

    repository = CohortRepository()
    result = repository.list(db_session, year=2099)

    result_ids = [c.id for c in result]
    assert target.id in result_ids
    assert other.id not in result_ids


def test_get_by_id_returns_existing_cohort(db_session, make_cohort):
    cohort = make_cohort(year=2026)

    repository = CohortRepository()
    result = repository.get_by_id(db_session, cohort.id)

    assert result is not None
    assert result.id == cohort.id


def test_get_by_id_returns_none_when_not_found(db_session):
    repository = CohortRepository()
    result = repository.get_by_id(db_session, 999999)

    assert result is None


def test_update_modifies_existing_cohort(db_session, make_cohort):
    cohort = make_cohort(year=2026, status="Active")

    repository = CohortRepository()
    payload = CohortUpsertRequest(
        id=cohort.id, year=2026, semester=1,
        start_date=date(2026, 3, 1), status="Closed",
    )
    updated = repository.update(db_session, cohort, payload)

    assert updated.status == "Closed"


def test_count_groups_returns_zero_when_no_groups(db_session, make_cohort):
    cohort = make_cohort(year=2026)

    repository = CohortRepository()
    count = repository.count_groups(db_session, cohort.id)

    assert count == 0