"""Tests for api/routes/health.py's Redis health check (issue #62)."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from api.routes.health import health_check
from core.config import settings


@pytest.mark.unit
class TestHealthCheckRedis:
    """Regression tests for the Redis branch of health_check()."""

    @pytest.fixture
    def mock_db(self):
        """A mock async DB session whose execute() succeeds (Postgres is
        not under test here)."""
        db = AsyncMock()
        db.execute = AsyncMock()
        return db

    def test_settings_has_no_redis_host_or_port(self):
        """Settings only ever exposed redis_url; the fix must not add
        redis_host/redis_port back as an alternate configuration path."""
        assert not hasattr(settings, "redis_host")
        assert not hasattr(settings, "redis_port")
        assert hasattr(settings, "redis_url")

    @pytest.mark.asyncio
    async def test_redis_healthy_uses_redis_url(self, mock_db):
        """health_check() must build its Redis client from settings.redis_url,
        not from the nonexistent redis_host/redis_port attributes."""
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True

        with patch("redis.Redis.from_url", return_value=mock_redis_client) as mock_from_url:
            result = await health_check(db=mock_db)

        mock_from_url.assert_called_once_with(settings.redis_url, decode_responses=True)
        assert result["dependencies"]["redis"] == "healthy"
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_redis_unhealthy_on_real_connection_failure(self, mock_db):
        """A genuine connection failure (not an AttributeError) must still
        be reported as unhealthy via the existing exception path."""
        mock_redis_client = Mock()
        mock_redis_client.ping.side_effect = ConnectionError("Connection refused")

        with (
            patch("redis.Redis.from_url", return_value=mock_redis_client),
            pytest.raises(HTTPException) as exc_info,
        ):
            await health_check(db=mock_db)

        detail = exc_info.value.detail
        assert detail["dependencies"]["redis"] == "unhealthy"
        assert detail["status"] == "unhealthy"
        assert exc_info.value.status_code == 503
