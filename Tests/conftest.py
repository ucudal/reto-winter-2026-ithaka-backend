from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.security import hash_password


@pytest.fixture
def mock_db():
    """Sesión de DB falsa: para tests de service/security que no deben tocar Postgres."""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_user():
    """Usuario de prueba con password conocida ('secret123')."""
    return User(
        id=1,
        name="Test User",
        email="test@ucu.edu.uy",
        role=UserRole.STUDENT,
        password_hash=hash_password("secret123"),
    )


@pytest.fixture
def sample_coordinator():
    """Usuario de prueba con rol Coordinator, para casos de permisos."""
    return User(
        id=2,
        name="Coord User",
        email="coord@ucu.edu.uy",
        role=UserRole.COORDINATOR,
        password_hash=hash_password("secret123"),
    )
