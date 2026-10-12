"""Tests for the Redis probe in api/routes/health.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthRedisProbe:
    """Test suite for the Redis health probe's client construction."""

    @pytest.mark.asyncio
    async def test_health_check_reports_redis_healthy_via_redis_url(self):
        """health_check() must build its Redis client from settings.redis_url,
        not the nonexistent redis_host/redis_port fields (issue #62)."""
        from core.config import settings

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=None)

        with patch("redis.Redis.from_url") as mock_from_url:
            mock_from_url.return_value = MagicMock(ping=MagicMock(return_value=True))

            result = await health_check(db=mock_db)

            assert result["dependencies"]["redis"] == "healthy"
            mock_from_url.assert_called_once_with(settings.redis_url, decode_responses=True)

    def test_redis_url_setting_exists(self):
        """Guard against regressing to the old host/port fields."""
        from core.config import settings

        assert hasattr(settings, "redis_url")
        assert not hasattr(settings, "redis_host")
        assert not hasattr(settings, "redis_port")
