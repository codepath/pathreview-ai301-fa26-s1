"""Tests for the dependency health endpoint."""

import pytest
import redis

from api.routes.health import health_check
from core.config import settings


class FakeDB:
    """Minimal healthy database dependency for the health check."""

    async def execute(self, _query):
        return None


@pytest.mark.asyncio
async def test_health_check_uses_configured_redis_url(monkeypatch):
    """Redis should be created from Settings.redis_url, not nonexistent host fields."""
    configured_url = "redis://redis.example.test:6380/4"
    calls = []

    class FakeRedis:
        def ping(self):
            return True

    def fake_from_url(url, **kwargs):
        calls.append((url, kwargs))
        return FakeRedis()

    monkeypatch.setattr(settings, "redis_url", configured_url)
    monkeypatch.setattr(redis.Redis, "from_url", fake_from_url)

    result = await health_check(FakeDB())

    assert result["status"] == "healthy"
    assert result["dependencies"]["redis"] == "healthy"
    assert calls == [(configured_url, {"decode_responses": True})]
