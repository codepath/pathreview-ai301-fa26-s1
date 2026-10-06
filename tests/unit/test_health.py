"""Tests for api/routes/health.py"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for the Redis branch of health_check()."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session that reports Postgres healthy."""
        session = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_redis_client_built_from_redis_url(self, mock_db_session):
        """health_check() must build the Redis client from settings.redis_url,
        not from the nonexistent redis_host/redis_port fields (issue #62)."""
        with patch("redis.Redis.from_url") as mock_from_url:
            mock_from_url.return_value = Mock(ping=Mock(return_value=True))

            await health_check(db=mock_db_session)

            mock_from_url.assert_called_once()
            args, kwargs = mock_from_url.call_args
            from core.config import settings

            assert args[0] == settings.redis_url
            assert kwargs.get("decode_responses") is True

    @pytest.mark.asyncio
    async def test_reports_healthy_when_redis_ping_succeeds(self, mock_db_session):
        """With a reachable Redis, the dependency must read 'healthy', not
        'unhealthy' from a swallowed AttributeError."""
        with patch("redis.Redis.from_url") as mock_from_url:
            mock_from_url.return_value = Mock(ping=Mock(return_value=True))

            result = await health_check(db=mock_db_session)

        assert result["dependencies"]["redis"] == "healthy"

    @pytest.mark.asyncio
    async def test_reports_unhealthy_when_redis_ping_fails(self, mock_db_session):
        """A real connection failure (not the missing-attribute bug) should
        still report unhealthy."""
        with patch("redis.Redis.from_url") as mock_from_url:
            mock_from_url.return_value = Mock(ping=Mock(side_effect=ConnectionError("refused")))

            with pytest.raises(HTTPException) as exc_info:
                await health_check(db=mock_db_session)

        assert exc_info.value.detail["dependencies"]["redis"] == "unhealthy"
