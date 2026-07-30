from __future__ import annotations
from datetime import date

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.db.session import engine
from app.core.models.cohort import Cohort


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