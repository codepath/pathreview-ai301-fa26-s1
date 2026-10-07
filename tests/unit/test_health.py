from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.sql.elements import TextClause

from api.routes.health import health_check


@pytest.mark.asyncio
async def test_health_check_uses_text_clause_for_postgres():
    mock_db = AsyncMock()

    mock_settings = Mock(
        redis_host="localhost",
        redis_port=6379,
        vector_db_url="http://localhost:8001",
    )

    with patch("redis.Redis") as mock_redis, patch("core.config.settings", mock_settings):
        mock_redis.return_value.ping.return_value = True

        result = await health_check(mock_db)

    mock_db.execute.assert_awaited_once()

    query = mock_db.execute.await_args.args[0]

    assert isinstance(query, TextClause)
    assert str(query) == "SELECT 1"
    assert result["dependencies"]["postgres"] == "healthy"
