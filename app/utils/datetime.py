from datetime import datetime, timezone


def utcnow() -> datetime:
    """Devuelve el datetime actual en UTC, con tzinfo explícito."""
    return datetime.now(timezone.utc)


def to_iso(dt: datetime) -> str:
    """Formatea un datetime a string ISO 8601."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def from_iso(value: str) -> datetime:
    """Parsea un string ISO 8601 a datetime."""
    return datetime.fromisoformat(value)
