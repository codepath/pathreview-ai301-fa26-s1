"""Regression tests for the SQLAlchemy-backed health-check database probe."""

from collections.abc import AsyncGenerator
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
import redis
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.routes import health
from core import config
from core.database import get_db

pytestmark = pytest.mark.unit


@pytest.fixture
def healthy_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the Redis/configuration issue separate from the database probe."""
    monkeypatch.setattr(
        config,
        "settings",
        SimpleNamespace(
            redis_host="localhost",
            redis_port=6379,
            vector_db_url="http://localhost:8001",
        ),
    )
    monkeypatch.setattr(redis, "Redis", Mock(return_value=Mock(ping=Mock(return_value=True))))


@pytest_asyncio.fixture
async def database_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a live SQLAlchemy session without requiring external services."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with AsyncSession(engine) as session:
            yield session
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_health_check_accepts_live_sqlalchemy_session(
    database_session: AsyncSession, healthy_dependencies: None
) -> None:
    """A reachable database must not be reported down by SQL text coercion."""
    control = await database_session.execute(text("SELECT 1"))
    assert control.scalar_one() == 1

    result = await health.health_check(db=database_session)

    assert result["status"] == "healthy"
    assert result["dependencies"]["postgres"] == "healthy"


@pytest.mark.asyncio
async def test_health_endpoint_returns_200_for_reachable_database(
    database_session: AsyncSession, healthy_dependencies: None
) -> None:
    """Exercise the production router with a live database dependency."""
    app = FastAPI()
    app.include_router(health.router)

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        yield database_session

    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["dependencies"]["postgres"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_preserves_503_for_database_failure(
    healthy_dependencies: None,
) -> None:
    """A real database error must still produce an unhealthy 503 response."""
    database = AsyncMock(spec=AsyncSession)
    database.execute.side_effect = OperationalError(
        "SELECT 1", {}, RuntimeError("database unavailable")
    )

    with pytest.raises(HTTPException) as raised:
        await health.health_check(db=database)

    assert raised.value.status_code == 503
    detail = raised.value.detail
    assert isinstance(detail, dict)
    assert detail["status"] == "unhealthy"
    assert detail["dependencies"]["postgres"] == "unhealthy"
    assert detail["dependencies"]["redis"] == "healthy"
