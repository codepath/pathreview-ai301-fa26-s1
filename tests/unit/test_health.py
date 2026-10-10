"""Tests for api/routes/health.py's health_check (issue #62)."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheckRedisProbe:
    """health_check's Redis probe must build its client from settings.redis_url,
    not the nonexistent settings.redis_host/settings.redis_port (issue #62)."""

    @pytest.fixture
    def mock_db(self):
        """A mock async DB session whose SELECT succeeds, so these tests
        isolate the Redis probe without depending on the separate,
        already-tracked postgres raw-SQL-string bug (issue #61)."""
        session = AsyncMock()
        session.execute = AsyncMock(return_value=Mock())
        return session

    @pytest.mark.asyncio
    async def test_redis_reachable_reports_healthy(self, mock_db):
        mock_client = Mock()
        mock_client.ping.return_value = True

        with patch("redis.Redis.from_url", return_value=mock_client) as mock_from_url:
            result = await health_check(db=mock_db)

        mock_from_url.assert_called_once_with(
            "redis://localhost:6379/0", decode_responses=True
        )
        assert result["dependencies"]["redis"] == "healthy"

    @pytest.mark.asyncio
    async def test_redis_unreachable_still_reports_unhealthy(self, mock_db):
        """The fix must not make the probe always report healthy: a real
        connection failure should still be caught and reported."""
        mock_client = Mock()
        mock_client.ping.side_effect = ConnectionError("Connection refused")

        with (
            patch("redis.Redis.from_url", return_value=mock_client),
            pytest.raises(HTTPException) as exc_info,
        ):
            await health_check(db=mock_db)

        assert exc_info.value.detail["dependencies"]["redis"] == "unhealthy"
