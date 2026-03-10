"""Hashtag count evaluator."""

import re
from typing import Any

from src.evaluators.base import BaseEvaluator, EvaluatorResult


class HashtagEvaluator(BaseEvaluator):
    """
    Evaluates hashtag usage in text.
    
    Checks if the text contains the required number of hashtags
    and optionally validates hashtag format.
    """

    # Pattern for valid hashtags
    HASHTAG_PATTERN = re.compile(r"#\w+", re.UNICODE)

    @property
    def name(self) -> str:
        return "hashtags"

    @property
    def description(self) -> str:
        return "Validates hashtag count and format"

    def evaluate(self, text: str, **kwargs: Any) -> EvaluatorResult:
        """
        Evaluate hashtag compliance.

        Args:
            text: Text to evaluate
            must_have_hashtags: Minimum required hashtags (default 0)
            max_hashtags: Maximum allowed hashtags (optional)

        Returns:
            EvaluatorResult with compliance score
        """
        min_hashtags = kwargs.get("must_have_hashtags", 0)
        max_hashtags = kwargs.get("max_hashtags")

        # Find all hashtags
        hashtags = self.HASHTAG_PATTERN.findall(text)
        hashtag_count = len(hashtags)

        # Check constraints
        has_minimum = hashtag_count >= min_hashtags
        within_maximum = max_hashtags is None or hashtag_count <= max_hashtags
        passed = has_minimum and within_maximum

        # Calculate score
        if passed:
            score = 1.0
        elif not has_minimum:
            # Partial score for having some hashtags
            score = hashtag_count / min_hashtags if min_hashtags > 0 else 0.0
        else:
            # Over maximum
            score = max(0.0, 1.0 - (hashtag_count - max_hashtags) / max_hashtags)  # type: ignore

        return EvaluatorResult(
            name=self.name,
            passed=passed,
            score=score,
            details={
                "hashtag_count": hashtag_count,
                "hashtags": hashtags,
                "min_required": min_hashtags,
                "max_allowed": max_hashtags,
                "has_minimum": has_minimum,
                "within_maximum": within_maximum,
            },
        )
