"""Check if generated feedback is supported by retrieved context."""

import re

import structlog

logger = structlog.get_logger()


class FaithfulnessChecker:
    """Verify that feedback claims are supported by context."""

    def check(self, feedback: str, context_chunks: list[dict]) -> float:
        """Check faithfulness of feedback to context.

        Args:
            feedback: Generated feedback text
            context_chunks: Retrieved context chunks

        Returns:
            Faithfulness score 0.0-1.0 (ratio of supported claims)
        """
        if not feedback or not context_chunks:
            logger.info(
                "faithfulness_empty_input",
                has_feedback=bool(feedback),
                has_chunks=bool(context_chunks),
            )
            return 0.0

        # Extract key claims from feedback (sentences)
        claims = self._extract_claims(feedback)
        if not claims:
            logger.info("faithfulness_no_claims_extracted")
            return 0.5  # Default to neutral if no extractable claims

        # Concatenate context text
        context_text = " ".join([chunk.get("text", "") for chunk in context_chunks])

        # Check each claim for support
        supported = 0
        for claim in claims:
            if self._is_supported(claim, context_text):
                supported += 1

        score = supported / len(claims) if claims else 0.0

        logger.info(
            "faithfulness_checked", claims_count=len(claims), supported_count=supported, score=score
        )

        return score

    @staticmethod
    def _extract_claims(text: str) -> list[str]:
        """Extract key claims from feedback text.

        Args:
            text: Feedback text

        Returns:
            List of claims (sentences or coordinated assertions)
        """
        sentences = re.split(r"[.!?]+", text)
        claims: list[str] = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            parts = re.split(r"\s*(?:,\s*and\s+|,\s*|\s+and\s+)\s*", sentence)
            claims.extend(part.strip() for part in parts if part.strip())

        return claims[:10]

    @staticmethod
    def _is_supported(claim: str, context: str) -> bool:
        """Check if a claim is supported by context.

        Args:
            claim: Claim text
            context: Context text

        Returns:
            True if claim is supported
        """
        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "and",
            "or",
            "but",
            "in",
            "of",
            "to",
            "for",
            "that",
            "developer",
            "has",
            "shows",
            "skills",
            "with",
        }

        claim_tokens = {
            token
            for token in re.findall(r"[a-z0-9+#]+(?:[.-][a-z0-9+#]+)*", claim.lower())
            if token not in stop_words
        }
        context_tokens = {
            token
            for token in re.findall(r"[a-z0-9+#]+(?:[.-][a-z0-9+#]+)*", context.lower())
            if token not in stop_words
        }

        if not claim_tokens:
            return False

        meaningful_overlap = claim_tokens & context_tokens
        return bool(meaningful_overlap)
