from __future__ import annotations
from datetime import date

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.db.session import engine
from app.core.models.cohort import Cohort
from app.core.models.group import Group


@pytest.fixture()
def db_session():
    """Sesion de test contra la base real, pero con rollback al final.

    Cada test corre dentro de una transaccion que se deshace al terminar,
    asi no quedan datos de prueba en la base.
    """
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
    """Crea una cohort de prueba. Un grupo necesita una cohort (FK)."""
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
    """Crea un grupo de prueba. Si no se pasa cohort_id, crea una cohort."""
    def _make_group(**overrides):
        if "cohort_id" not in overrides:
            overrides["cohort_id"] = make_cohort().id

        defaults = {
            "name": "EcoRoute",
            "idea": "",
            "status": "Active",
        }
        defaults.update(overrides)
        group = Group(**defaults)
        db_session.add(group)
        db_session.flush()
        return group
    return _make_group