from __future__ import annotations

from app.core.repositories.group_repository import GroupRepository


def test_list_returns_groups_filtered_by_cohort(db_session, make_group, make_cohort):
    cohort_a = make_cohort(year=2099)  # año poco comun, evita chocar con el seeder
    cohort_b = make_cohort(year=2098)
    target = make_group(name="EcoRoute", cohort_id=cohort_a.id)
    other = make_group(name="AgroSmart", cohort_id=cohort_b.id)

    repository = GroupRepository()
    result = repository.list(db_session, cohort_id=cohort_a.id)

    result_ids = [g.id for g in result]
    assert target.id in result_ids
    assert other.id not in result_ids


def test_get_by_id_returns_existing_group(db_session, make_group):
    group = make_group(name="EcoRoute")

    repository = GroupRepository()
    result = repository.get_by_id(db_session, group.id)

    assert result is not None
    assert result.id == group.id


def test_get_by_id_returns_none_when_not_found(db_session):
    repository = GroupRepository()
    result = repository.get_by_id(db_session, 999999)

    assert result is None


def test_list_filters_by_status(db_session, make_group):
    active = make_group(name="ActiveGroup", status="Active")
    inactive = make_group(name="InactiveGroup", status="Inactive")

    repository = GroupRepository()
    result = repository.list(db_session, status="Active")

    result_ids = [g.id for g in result]
    assert active.id in result_ids
    assert inactive.id not in result_ids


def test_list_filters_by_search(db_session, make_group):
    match = make_group(name="EcoRoute")
    no_match = make_group(name="AgroSmart")

    repository = GroupRepository()
    result = repository.list(db_session, search="eco")  # ilike, no distingue mayus

    result_ids = [g.id for g in result]
    assert match.id in result_ids
    assert no_match.id not in result_ids