"""Tests for api/routes/reviews.py"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks

from api.routes.reviews import create_review_endpoint
from api.schemas.review import ReviewCreate


@pytest.mark.unit
class TestReviewRoutes:
    """Test suite for api/routes/reviews.py"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def mock_current_user(self):
        """Create a mock authenticated user."""
        user = Mock()
        user.id = uuid4()
        return user

    @pytest.fixture
    def mock_review(self):
        """Create a mock Review object returned by create_review."""
        review = Mock()
        review.id = uuid4()
        review.profile_id = uuid4()
        review.status = "pending"
        review.sections = None
        review.overall_score = None
        return review

    @pytest.mark.asyncio
    @pytest.mark.xfail(
        strict=True,
        reason=(
            "issue #36: POST /reviews should validate that a profile has "
            "ingested documents before accepting a review and return 422 "
            "when it has none, per @Kunalkrk's proposed approach. Currently "
            "the endpoint accepts the request unconditionally."
        ),
    )
    async def test_create_review_for_profile_with_no_ingested_documents_returns_422(
        self, mock_db_session, mock_current_user, mock_review
    ):
        """
        A profile with no ingested documents (no github_username, no
        portfolio_url, no resume_text) should cause POST /reviews to return
        a 422 error rather than silently accepting the request and later
        completing with fabricated feedback (see issue #36 repro).
        """
        profile_id_with_no_sources = uuid4()
        data = ReviewCreate(profile_id=profile_id_with_no_sources)
        background_tasks = BackgroundTasks()

        with patch("api.routes.reviews.create_review", new=AsyncMock(return_value=mock_review)):
            with pytest.raises(Exception) as exc_info:
                await create_review_endpoint(
                    data=data,
                    background_tasks=background_tasks,
                    current_user=mock_current_user,
                    db=mock_db_session,
                )

            assert getattr(exc_info.value, "status_code", None) == 422
