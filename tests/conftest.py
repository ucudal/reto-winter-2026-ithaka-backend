from __future__ import annotations
from datetime import date

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.db.session import engine
from app.core.models.cohort import Cohort
from app.core.models.group import Group
from app.core.models.checkpoint import Checkpoint


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    TestSessionLocal = sessionmaker(bind=connection)
    session: Session = TestSessionLocal()

    session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def make_cohort(db_session):
    def _make_cohort(**overrides):
        defaults = {
            "year": 2026,
            "semester": 1,
            "start_date": date(2026, 3, 1),
            "status": "Active",
        }
        defaults.update(overrides)
        cohort = Cohort(**defaults)
        db_session.add(cohort)
        db_session.flush()
        return cohort

    return _make_cohort


@pytest.fixture()
def make_group(db_session, make_cohort):
    def _make_group(**overrides):
        cohort = overrides.pop("cohort", None) or make_cohort()
        defaults = {
            "name": "Test Group",
            "cohort_id": cohort.id,
            "status": "Active",
        }
        defaults.update(overrides)
        group = Group(**defaults)
        db_session.add(group)
        db_session.flush()
        return group

    return _make_group


@pytest.fixture()
def make_checkpoint(db_session, make_group):
    def _make_checkpoint(**overrides):
        group = overrides.pop("group", None) or make_group()
        defaults = {
            "group_id": group.id,
            "cohort_id": group.cohort_id,
            "title": "Checkpoint de prueba",
            "due_date": date(2026, 6, 1),
            "status": "Pending",
            "questions": [],
        }
        defaults.update(overrides)
        checkpoint = Checkpoint(**defaults)
        db_session.add(checkpoint)
        db_session.flush()
        return checkpoint

    return _make_checkpoint