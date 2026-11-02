"""Tests for the safety event count in api/routes/health.py"""

from unittest.mock import Mock

import pytest
import redis

from api.routes.health import _count_safety_events


@pytest.mark.unit
class TestCountSafetyEvents:
    """Test suite for _count_safety_events."""

    def test_sums_counts_across_event_types(self):
        """Test counts from every event type are added together."""
        counts = {
            "safety:events:pii_detected": "2",
            "safety:events:injection_attempt": "1",
        }
        mock_redis = Mock()
        mock_redis.get = Mock(side_effect=counts.get)

        assert _count_safety_events(mock_redis) == 3

    def test_no_events_returns_zero(self):
        """Test zero is returned when no counters exist."""
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=None)

        assert _count_safety_events(mock_redis) == 0

    def test_redis_error_returns_zero(self):
        """Test a Redis error yields zero instead of raising."""
        mock_redis = Mock()
        mock_redis.get = Mock(side_effect=redis.ConnectionError("down"))

        assert _count_safety_events(mock_redis) == 0
