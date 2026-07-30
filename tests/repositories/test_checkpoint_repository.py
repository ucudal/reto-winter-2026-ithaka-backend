from __future__ import annotations

from app.core.repositories.checkpoint_repository import CheckpointRepository


def test_list_returns_checkpoints_filtered_by_group(db_session, make_checkpoint, make_group):
    group = make_group()
    target = make_checkpoint(group=group)
    other = make_checkpoint()  # otro grupo, no debería aparecer

    repository = CheckpointRepository()
    result = repository.list(db_session, group_id=group.id)

    result_ids = [c.id for c in result]
    assert target.id in result_ids
    assert other.id not in result_ids


def test_list_filters_by_search_on_group_name(db_session, make_checkpoint, make_group):
    group = make_group(name="EcoRoute")
    target = make_checkpoint(group=group)

    repository = CheckpointRepository()
    result = repository.list(db_session, search="EcoRoute")

    result_ids = [c.id for c in result]
    assert target.id in result_ids


def test_get_by_id_returns_existing_checkpoint(db_session, make_checkpoint):
    checkpoint = make_checkpoint()

    repository = CheckpointRepository()
    result = repository.get_by_id(db_session, checkpoint.id)

    assert result is not None
    assert result.id == checkpoint.id


def test_get_by_id_returns_none_when_not_found(db_session):
    repository = CheckpointRepository()
    result = repository.get_by_id(db_session, 999999)

    assert result is None


def test_update_modifies_existing_checkpoint(db_session, make_checkpoint):
    checkpoint = make_checkpoint(status="Pending")

    repository = CheckpointRepository()
    updated = repository.update(db_session, checkpoint, {"status": "Closed"})

    assert updated.status == "Closed"


def test_update_ignores_none_values(db_session, make_checkpoint):
    checkpoint = make_checkpoint(title="Original title", status="Pending")

    repository = CheckpointRepository()
    updated = repository.update(db_session, checkpoint, {"title": None, "status": "Closed"})

    assert updated.title == "Original title"
    assert updated.status == "Closed"