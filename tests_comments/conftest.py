import pytest
from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db.base import Base

from app.core.models.user import User
from app.core.models.cohort import Cohort
from app.core.models.stage import Stage
from app.core.models.tutor import Tutor
from app.core.models.group import Group
from app.core.models.student import Student
from app.core.models.deliverable import Deliverable
from app.core.models.meeting import Meeting
from app.core.models.document import Document
from app.core.models.comment import Comment
from app.core.models.support_material import SupportMaterial


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw):
    return compiler.visit_JSON(JSON(), **kw)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()