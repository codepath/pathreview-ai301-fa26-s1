"""Tests for the /health endpoint's safety event count."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from api.routes.health import health_check


def _run_health_check() -> dict:
    """Call the handler directly; other probes may fail in a unit context, so read the 503 detail too."""
    try:
        return asyncio.run(health_check(db=AsyncMock()))
    except HTTPException as exc:
        return exc.detail


@pytest.mark.unit
class TestHealthSafetyEventCount:
    def test_reports_sum_of_monitor_counts(self):
        counts = {
            "safety:events:pii_detected": b"2",
            "safety:events:injection_attempt": b"1",
        }
        fake_redis = Mock()
        fake_redis.get.side_effect = counts.get

        with patch("redis.Redis.from_url", return_value=fake_redis):
            body = _run_health_check()

        assert body["safety_events_last_hour"] == 3

    def test_reports_zero_when_redis_errors(self):
        fake_redis = Mock()
        fake_redis.get.side_effect = ConnectionError("redis down")

        with patch("redis.Redis.from_url", return_value=fake_redis):
            body = _run_health_check()

        assert body["safety_events_last_hour"] == 0
