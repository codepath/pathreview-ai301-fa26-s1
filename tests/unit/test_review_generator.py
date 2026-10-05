"""Tests for review_generator.py"""

import json
from unittest.mock import MagicMock

import pytest

from rag.generator.review_generator import (
    MAX_GENERATION_ATTEMPTS,
    ReviewConfig,
    ReviewGenerator,
)


def make_completion(content: str | None) -> MagicMock:
    """Build a mock OpenAI chat completion response with the given content."""
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    return response


def make_section_payload(section_name: str, content: str) -> str:
    """Build a JSON-fenced payload parseable into a single FeedbackSection."""
    return "```json\n" + json.dumps({section_name: content}) + "\n```"


@pytest.fixture
def generator() -> ReviewGenerator:
    """Create a ReviewGenerator with a mocked OpenAI-compatible client."""
    config = ReviewConfig(api_key="test-key", base_url="https://example.test", model="test-model")
    gen = ReviewGenerator(config)
    gen.client = MagicMock()
    return gen


@pytest.mark.unit
class TestReviewGeneratorToneCheck:
    """Test suite for the post-generation tone check in generate_section."""

    def test_constructive_first_pass_accepted_without_regeneration(self, generator):
        """A constructive classification accepts the first generated section."""
        payload = make_section_payload("skills_feedback", "Great use of testing patterns.")
        generator.client.chat.completions.create.side_effect = [
            make_completion(payload),
            make_completion("constructive"),
        ]

        section = generator.generate_section("skills_feedback", [], {"projects": []})

        assert section.content == "Great use of testing patterns."
        assert generator.client.chat.completions.create.call_count == 2

    def test_negative_section_is_regenerated_and_constructive_retry_returned(self, generator):
        """A negative classification rejects the first section and returns the retry."""
        rejected_payload = make_section_payload("skills_feedback", "Your code is garbage.")
        accepted_payload = make_section_payload(
            "skills_feedback", "Consider adding tests to strengthen this section."
        )
        generator.client.chat.completions.create.side_effect = [
            make_completion(rejected_payload),
            make_completion("negative"),
            make_completion(accepted_payload),
            make_completion("constructive"),
        ]

        section = generator.generate_section("skills_feedback", [], {"projects": []})

        assert section.content == "Consider adding tests to strengthen this section."
        assert generator.client.chat.completions.create.call_count == 4

    def test_repeated_negative_classifications_stop_at_three_attempts(self, generator):
        """Repeated negative classifications exhaust the retry limit without leaking content."""
        payload = make_section_payload("skills_feedback", "Your code is garbage.")
        generator.client.chat.completions.create.side_effect = [
            make_completion(payload),
            make_completion("negative"),
            make_completion(payload),
            make_completion("negative"),
            make_completion(payload),
            make_completion("negative"),
        ]

        with pytest.raises(RuntimeError, match="skills_feedback"):
            generator.generate_section("skills_feedback", [], {"projects": []})

        assert generator.client.chat.completions.create.call_count == MAX_GENERATION_ATTEMPTS * 2

    def test_malformed_classification_is_not_treated_as_constructive(self, generator):
        """An unexpected classifier response follows the same bounded failure path."""
        payload = make_section_payload("skills_feedback", "Your code is garbage.")
        generator.client.chat.completions.create.side_effect = [
            make_completion(payload),
            make_completion("maybe constructive, hard to say"),
            make_completion(payload),
            make_completion(""),
            make_completion(payload),
            make_completion(None),
        ]

        with pytest.raises(RuntimeError, match="after 3 generation attempts"):
            generator.generate_section("skills_feedback", [], {"projects": []})

        assert generator.client.chat.completions.create.call_count == MAX_GENERATION_ATTEMPTS * 2

    def test_classification_prompt_contains_section_and_criteria(self, generator):
        """The classification call includes the candidate section and the issue's criteria."""
        payload = make_section_payload("skills_feedback", "Consider documenting your API.")
        generator.client.chat.completions.create.side_effect = [
            make_completion(payload),
            make_completion("constructive"),
        ]

        generator.generate_section("skills_feedback", [], {"projects": []})

        classification_call = generator.client.chat.completions.create.call_args_list[1]
        classification_prompt = classification_call.kwargs["messages"][1]["content"]

        assert "Consider documenting your API." in classification_prompt
        assert "actionable" in classification_prompt
        assert "specific" in classification_prompt
        assert "encouraging" in classification_prompt
        assert "discouraging" in classification_prompt
        assert "vague" in classification_prompt
        assert "dismissive" in classification_prompt

    def test_classification_reuses_generator_client_and_model(self, generator):
        """The tone check is issued against the generator's own client and configured model."""
        payload = make_section_payload("skills_feedback", "Consider documenting your API.")
        generator.client.chat.completions.create.side_effect = [
            make_completion(payload),
            make_completion("constructive"),
        ]

        generator.generate_section("skills_feedback", [], {"projects": []})

        generation_call, classification_call = generator.client.chat.completions.create.call_args_list
        assert generation_call.kwargs["model"] == generator.config.model
        assert classification_call.kwargs["model"] == generator.config.model
