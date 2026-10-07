import asyncio
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis

from api.routes.health import health_check

pytestmark = pytest.mark.unit


def _run_health():
    db = MagicMock()
    db.execute = AsyncMock()
    return asyncio.run(health_check(db=db))


def test_redis_client_built_from_redis_url_and_reported_healthy():
    client = MagicMock()
    with patch("redis.Redis.from_url", return_value=client) as from_url:
        result = _run_health()
    from_url.assert_called_once()
    assert from_url.call_args.args[0].startswith("redis://")
    client.ping.assert_called_once()
    body = result if isinstance(result, dict) else result.body
    assert body["dependencies"]["redis"] == "healthy"


def test_unreachable_redis_is_unhealthy_via_connection_error_not_attribute_error():
    client = MagicMock()
    client.ping.side_effect = redis.exceptions.ConnectionError("refused")
    with patch("redis.Redis.from_url", return_value=client), patch(
        "api.routes.health.log"
    ) as log:
        with pytest.raises(HTTPException) as exc_info:
            _run_health()
    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["dependencies"]["redis"] == "unhealthy"
    error_calls = [c for c in log.error.call_args_list if c.args[0] == "redis_health_check_failed"]
    assert error_calls and "refused" in error_calls[0].kwargs["error"]
