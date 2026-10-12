"""Shared test fixtures for PathReview."""

import pytest
import structlog


@pytest.fixture(autouse=True)
def structlog_to_stdlib():
    """Route structlog events into stdlib logging so pytest's caplog sees them.

    Without configuration, structlog's default logger prints straight to
    stdout and bypasses the stdlib logging system that caplog hooks into
    (issue #66). Each event is rendered to a plain string so no key-value
    pair is passed as ``extra``, where a key like ``name`` would clash with
    a built-in LogRecord attribute.
    """
    structlog.configure(
        processors=[structlog.dev.ConsoleRenderer(colors=False)],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )
    yield
    structlog.reset_defaults()


@pytest.fixture
def sample_resume_text() -> str:
    """Return a sample resume text for testing."""
    return """
    Jane Doe
    Software Engineer
    jane.doe@example.com | github.com/janedoe

    Experience:
    - Software Engineer at TechCorp (2022-2024)
      Built REST APIs using Python and FastAPI.

    Education:
    - B.S. Computer Science, State University (2022)

    Skills: Python, JavaScript, React, PostgreSQL, Docker
    """


@pytest.fixture
def sample_readme_text() -> str:
    """Return a sample README text for testing."""
    return """
    # Weather App
    A weather forecasting application built with React and OpenWeatherMap API.

    ## Features
    - Current weather display
    - 5-day forecast
    - Location search

    ## Tech Stack
    - React 18
    - TypeScript
    - Tailwind CSS
    - OpenWeatherMap API
    """
