"""Tests for api/routes/health.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.routes.health import health_check


@pytest.mark.unit
@pytest.mark.asyncio
async def test_redis_health_check_uses_redis_url():
    """Redis probe should connect via settings.redis_url (issue #62)."""
    db = AsyncMock()
    db.execute = AsyncMock()

    mock_redis = MagicMock()
    mock_redis.ping.return_value = True

    with patch("redis.Redis.from_url", return_value=mock_redis) as from_url:
        result = await health_check(db=db)

    from_url.assert_called_once()
    assert from_url.call_args[0][0] == "redis://localhost:6379/0"
    assert result["dependencies"]["redis"] == "healthy"
