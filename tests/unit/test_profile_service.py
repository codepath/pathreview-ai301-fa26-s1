"""Tests for profile_service.py"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from core.services.profile_service import delete_profile
from rag.retriever.vector_store import VectorStore


def _make_chunk(chunk_id: str):
    return SimpleNamespace(
        id=chunk_id, text="Sample resume text.", source_id="resume_abc", chunk_index=0, section=None
    )


def _collection_exists(store: VectorStore, name: str) -> bool:
    return name in [c.name for c in store.client.list_collections()]


@pytest.mark.unit
class TestDeleteProfile:
    """Test suite for delete_profile vector store cleanup."""

    @pytest.fixture
    def store(self, tmp_path):
        """A real VectorStore persisted in a temp directory."""
        return VectorStore(persist_dir=str(tmp_path))

    @pytest.fixture
    def mock_db_session(self):
        """Mock async session whose lookups find a profile and no related rows."""
        profile = Mock()
        profile_result = Mock()
        profile_result.scalars.return_value.first.return_value = profile
        empty_result = Mock()
        empty_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[profile_result, empty_result, empty_result])
        session.delete = AsyncMock()
        session.commit = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_deletes_profile_collection(self, mock_db_session, store):
        """The profile's collection is gone after delete_profile returns True."""
        profile_id, user_id = uuid4(), uuid4()
        name = f"profile_{profile_id}"
        store.add_chunks([(_make_chunk("resume_abc_chunk_0"), [0.1] * 8)], name)
        other = f"profile_{uuid4()}"
        store.add_chunks([(_make_chunk("resume_xyz_chunk_0"), [0.1] * 8)], other)
        assert _collection_exists(store, name)

        result = await delete_profile(mock_db_session, profile_id, user_id, vector_store=store)

        assert result is True
        assert not _collection_exists(store, name)
        assert _collection_exists(store, other)

    @pytest.mark.asyncio
    async def test_profile_without_collection_still_deleted(self, mock_db_session, store):
        """A profile that was never ingested has no collection and still deletes."""
        profile_id = uuid4()

        result = await delete_profile(mock_db_session, profile_id, uuid4(), vector_store=store)

        assert result is True
        assert not _collection_exists(store, f"profile_{profile_id}")

    @pytest.mark.asyncio
    async def test_vector_cleanup_failure_does_not_fail_delete(self, mock_db_session):
        """If the vector cleanup raises, the committed delete still returns True."""
        failing_store = Mock()
        failing_store.delete_collection.side_effect = RuntimeError("chroma down")

        result = await delete_profile(mock_db_session, uuid4(), uuid4(), vector_store=failing_store)

        assert result is True
        mock_db_session.commit.assert_awaited_once()
