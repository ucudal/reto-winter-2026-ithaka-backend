"""Fixtures compartidas para los tests de autenticacion y permisos.

Las variables de entorno se setean ANTES de importar cualquier modulo de `app`,
porque `app.core.config` las lee en tiempo de import.
"""
from __future__ import annotations

import os

SECRET = "test-secret-key-solo-para-tests-32b"

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = SECRET
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# SQLite no conoce JSONB (es de PostgreSQL). Lo mapeamos a JSON solo para tests,
# asi podemos crear el schema completo en memoria.
@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw):  # noqa: ANN001, ANN003
    return compiler.visit_JSON(JSON(), **kw)


from app.core.db.base import Base  # noqa: E402
from app.core.db.session import get_db  # noqa: E402
from app.core.models import User  # noqa: E402  (registra todos los modelos)
from app.core.models.enums import UserRole  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402


PASSWORD = "password123"

# name, email, role. El orden fija los ids: coordinator=1 ... student=4.
USUARIOS = {
    "coordinator": ("Coord Ithaka", "coord@ucu.edu.uy", UserRole.COORDINATOR),
    "business_tutor": ("Maria Perez", "maria@ucu.edu.uy", UserRole.BUSINESS_TUTOR),
    "technical_tutor": ("Diego Ramirez", "diego@ucu.edu.uy", UserRole.TECHNICAL_TUTOR),
    "student": ("Ana Fernandez", "ana@ucu.edu.uy", UserRole.STUDENT),
}


@pytest.fixture(scope="session")
def password_hash() -> str:
    """bcrypt es lento a proposito: lo calculamos una sola vez para toda la corrida."""
    return hash_password(PASSWORD)


def _nueva_base(password_hash: str):
    """Motor SQLite en memoria con el schema completo y un usuario por rol."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as db:
        db.add_all(
            User(name=n, email=e, role=r, password_hash=password_hash)
            for n, e, r in USUARIOS.values()
        )
        db.commit()
    return engine, factory


def _cliente(factory):
    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    # raise_server_exceptions=False: a estos tests les importa la capa de auth,
    # no que el endpoint encuentre datos. Un 500 por base vacia es un resultado
    # valido: significa que el request paso el guard.
    return TestClient(fastapi_app, raise_server_exceptions=False)


@pytest.fixture
def client(password_hash):
    """Base nueva por test: los DELETE/PUT de un test no ensucian al siguiente."""
    engine, factory = _nueva_base(password_hash)
    with _cliente(factory) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture(scope="session")
def tokens(password_hash) -> dict[str, str]:
    """Un token JWT real por rol, emitido una sola vez via POST /api/auth/login.

    Sirve para toda la corrida porque el claim `sub` es el id del usuario y el
    seed siempre genera los mismos ids.
    """
    engine, factory = _nueva_base(password_hash)
    try:
        with _cliente(factory) as c:
            resultado = {}
            for rol, (_n, email, _r) in USUARIOS.items():
                resp = c.post("/api/auth/login", json={"email": email, "password": PASSWORD})
                assert resp.status_code == 200, resp.text
                resultado[rol] = resp.json()["token"]
            return resultado
    finally:
        fastapi_app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture
def headers(tokens) -> dict[str, dict[str, str]]:
    """Header Authorization armado para cada rol."""
    return {rol: {"Authorization": f"Bearer {t}"} for rol, t in tokens.items()}


def sembrar_dominio(factory) -> None:
    """Carga un cohorte completo: etapa, tutor, grupo, alumno, entregable, etc.

    Sirve para los tests de "acceso autorizado", donde queremos ver un 200 real
    y no un 404 por base vacia.
    """
    from datetime import date, datetime, timezone

    from app.core.models.cohort import Cohort
    from app.core.models.comment import Comment
    from app.core.models.deliverable import Deliverable
    from app.core.models.document import Document
    from app.core.models.enums import DocumentPlatform, EntityType, TutorRole
    from app.core.models.meeting import MeetingStatus
    from app.core.models.group import Group
    from app.core.models.meeting import Meeting
    from app.core.models.stage import Stage
    from app.core.models.student import Student
    from app.core.models.support_material import SupportMaterial
    from app.core.models.tutor import Tutor

    with factory() as db:
        cohorte = Cohort(year=2026, semester=1, start_date=date(2026, 3, 1),
                         end_date=date(2026, 7, 15), status="Active")
        db.add(cohorte); db.flush()

        etapa = Stage(cohort_id=cohorte.id, name="Ideacion", order=1, key_dates=[])
        db.add(etapa); db.flush()

        tutor_neg = Tutor(name="Maria Perez", role=TutorRole.BUSINESS, max_capacity=88,
                          user_id=2, status="Active")
        tutor_tec = Tutor(name="Diego Ramirez", role=TutorRole.TECHNICAL, max_capacity=88,
                          user_id=3, status="Active")
        db.add_all([tutor_neg, tutor_tec]); db.flush()

        grupo = Group(name="EcoRoute", cohort_id=cohorte.id, current_stage_id=etapa.id,
                      idea="Rutas de reciclaje", status="Active",
                      business_tutor_id=tutor_neg.id, technical_tutor_id=tutor_tec.id)
        db.add(grupo); db.flush()

        db.add(Student(name="Ana Fernandez", email="ana.f@ucu.edu.uy",
                       major="Ingenieria de Sistemas", group_id=grupo.id, user_id=4))

        entregable = Deliverable(group_id=grupo.id, stage_id=etapa.id,
                                 expected_date=date(2026, 4, 20), status="Pending")
        db.add(entregable); db.flush()

        db.add_all([
            Comment(tutor_id=tutor_neg.id, deliverable_id=entregable.id,
                    content="Falta analisis competitivo"),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=entregable.id,
                     url="https://drive.google.com/doc", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=grupo.id,
                     url="https://drive.google.com/repo", platform=DocumentPlatform.DRIVE, order=1),
            SupportMaterial(stage_id=etapa.id, title="Business Model Canvas",
                            url="https://drive.google.com/bmc"),
            Meeting(group_id=grupo.id, tutor_ids=[tutor_neg.id],
                    status=MeetingStatus.HELD,
                    date=datetime(2026, 4, 10, 15, 0, tzinfo=timezone.utc),
                    participants=[], hours_spent=1.5, links=[]),
        ])
        db.commit()


@pytest.fixture
def client_con_datos(password_hash):
    """Como `client`, pero con un cohorte completo cargado."""
    engine, factory = _nueva_base(password_hash)
    sembrar_dominio(factory)
    with _cliente(factory) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
    engine.dispose()