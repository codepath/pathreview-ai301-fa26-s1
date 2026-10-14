"""Tests for the Postgres probe in api/routes/health.py"""

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from api.routes.health import health_check


class _SyncSessionAdapter:
    """Expose a real sync SQLAlchemy Session through the async ``execute`` the route awaits.

    A Mock would accept any argument, including the bare string issue #61 is about.
    A real Session runs SQLAlchemy's statement coercion, so it rejects that string
    with the same ArgumentError the route hits against Postgres.
    """

    def __init__(self, session: Session):
        self._session = session

    async def execute(self, statement):
        """Run ``statement`` on the wrapped session."""
        return self._session.execute(statement)


class _FailingSession:
    """A session whose database is unreachable."""

    async def execute(self, statement):
        """Raise the error a dropped connection would."""
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


async def _postgres_status(db) -> str:
    """Return the postgres dependency status, whether the route returns or raises 503.

    The Redis probe in the same route fails independently (issue #62), so the route
    may raise 503 even when Postgres is healthy; read the postgres key either way.
    """
    try:
        result = await health_check(db=db)
    except HTTPException as exc:
        result = exc.detail
    return result["dependencies"]["postgres"]


@pytest.mark.unit
class TestHealthPostgresProbe:
    """Test suite for the Postgres branch of health_check()."""

    @pytest.fixture
    def sqlite_session(self):
        """Create a real SQLAlchemy session on an in-memory SQLite database."""
        engine = create_engine("sqlite://")
        with Session(engine) as session:
            yield _SyncSessionAdapter(session)
        engine.dispose()

    @pytest.mark.asyncio
    async def test_postgres_probe_reports_healthy_for_reachable_db(self, sqlite_session):
        """A reachable database must read 'healthy' (issue #61)."""
        assert await _postgres_status(sqlite_session) == "healthy"

    @pytest.mark.asyncio
    async def test_postgres_probe_reports_unhealthy_when_db_errors(self):
        """A database error must still read 'unhealthy'."""
        assert await _postgres_status(_FailingSession()) == "unhealthy"
