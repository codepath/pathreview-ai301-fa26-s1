"""Content filter for generated feedback."""

import re

import openai
import structlog

logger = structlog.get_logger()

TONE_CLASSIFICATION_PROMPT = """Classify the following portfolio review feedback as either \
"constructive" or "negative".

Constructive feedback is actionable, specific, and encouraging.
Negative feedback is discouraging, vague, or dismissive.

Feedback:
{section_content}

Respond with exactly one word: constructive or negative."""


class ContentFilter:
    """Filter genuinely harmful content from generated feedback."""

    # Specific harmful patterns (not broad keyword matching)
    HARMFUL_PATTERNS = [
        r"(?:kill|harm|hurt)\s+(?:yourself|yourself|themself|themselves)",
        r"(?:suicide|self-harm|cut\s+yourself)",
        r"(?:hate|despise)\s+(?:themself|themselves|yourself)",
        r"(?:worthless|useless|trash|garbage)\s+(?:person|human)",
        r"(?:illegal|unlawful)\s+(?:activity|action|conduct)",
        r"(?:child|minor)\s+(?:abuse|exploitation|trafficking)",
    ]

    @staticmethod
    def filter(text: str) -> tuple[str, bool]:
        """Filter harmful content from text.

        Args:
            text: Text to filter

        Returns:
            Tuple of (filtered_text, was_filtered)
        """
        was_filtered = False
        filtered_text = text

        for pattern in ContentFilter.HARMFUL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("harmful_content_detected", pattern=pattern)
                was_filtered = True
                # Replace harmful phrases with neutral text
                filtered_text = re.sub(
                    pattern, "[CONTENT REMOVED]", filtered_text, flags=re.IGNORECASE
                )

        return filtered_text, was_filtered

    @staticmethod
    def is_constructive(client: openai.OpenAI, model: str, section_content: str) -> bool:
        """Classify generated feedback as constructive or negative in tone.

        Args:
            client: OpenAI-compatible client to issue the classification call with.
            model: Model identifier to use for the classification call.
            section_content: Generated feedback section text to classify.

        Returns:
            True only if the classifier returns the normalized "constructive"
            label; negative and unexpected responses both return False.
        """
        prompt = TONE_CLASSIFICATION_PROMPT.format(section_content=section_content)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a feedback tone classifier."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        raw_label = response.choices[0].message.content or ""
        normalized = raw_label.strip().lower()

        if normalized != "constructive":
            logger.warning("tone_check_rejected", raw_label=raw_label)
            return False

        return True
