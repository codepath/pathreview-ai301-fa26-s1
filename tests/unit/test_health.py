"""Regression test for issue #62: the Redis probe read settings.redis_host,
which Settings does not define, so the probe always reported Redis down."""

from unittest.mock import MagicMock, patch

import pytest

from api.routes.health import health_check
from core.config import settings


class _FakeDB:
    async def execute(self, *_args, **_kwargs):
        return None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_redis_probe_uses_configured_redis_url():
    with patch("redis.from_url", return_value=MagicMock()) as from_url:
        result = await health_check(db=_FakeDB())

    from_url.assert_called_once()
    assert from_url.call_args.args[0] == settings.redis_url
    assert result["dependencies"]["redis"] == "healthy"
