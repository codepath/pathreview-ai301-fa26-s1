"""Unit tests for ingestion pipeline deduplication and check_skip behavior."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.models.ingested_source import IngestedSource
from ingestion.pipeline import IngestionPipeline


@pytest.fixture
def db_session():
    """Create an in-memory SQLite session with ingested_sources table created."""
    engine = create_engine("sqlite:///:memory:")
    IngestedSource.__table__.create(engine, checkfirst=True)
    with Session(engine) as session:
        yield session
    IngestedSource.__table__.drop(engine, checkfirst=True)


@pytest.mark.unit
def test_check_skip_returns_none_when_source_not_present(db_session):
    """When source has not been ingested, _check_skip should return None without error."""
    pipeline = IngestionPipeline(
        db_session=db_session,
        vector_db=MagicMock(),
        embedding_provider=MagicMock(),
    )
    result = pipeline._check_skip("non-existent-source", "repo")
    assert result is None


@pytest.mark.unit
def test_check_skip_skips_when_source_already_ingested(db_session):
    """When source_id exists in IngestedSource, _check_skip returns skipped=True."""
    source = IngestedSource(
        id=str(uuid4()),
        source_id="test-source-123",
        source_type="repo",
        profile_id=str(uuid4()),
        chunk_count=5,
    )
    db_session.add(source)
    db_session.commit()

    pipeline = IngestionPipeline(
        db_session=db_session,
        vector_db=MagicMock(),
        embedding_provider=MagicMock(),
    )
    result = pipeline._check_skip("test-source-123", "repo")
    assert result is not None
    assert result.skipped is True
    assert result.source_id == "test-source-123"
    assert result.skip_reason == "Source already ingested"
    assert result.chunk_count == 0


@pytest.mark.unit
def test_record_ingested_source_persists_to_database(db_session):
    """_record_ingested_source stores the row in db_session."""
    pipeline = IngestionPipeline(
        db_session=db_session,
        vector_db=MagicMock(),
        embedding_provider=MagicMock(),
    )
    profile_id = str(uuid4())
    pipeline._record_ingested_source("persisted-id-456", "resume", profile_id, 3)

    stored = db_session.query(IngestedSource).filter_by(source_id="persisted-id-456").first()
    assert stored is not None
    assert stored.source_id == "persisted-id-456"
    assert stored.chunk_count == 3
