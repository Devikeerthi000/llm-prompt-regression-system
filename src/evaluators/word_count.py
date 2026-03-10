"""Word count evaluator."""

from typing import Any

from src.evaluators.base import BaseEvaluator, EvaluatorResult


class WordCountEvaluator(BaseEvaluator):
    """
    Evaluates text against word count constraints.
    
    Checks if the text length is within specified minimum and maximum bounds.
    """

    @property
    def name(self) -> str:
        return "word_count"

    @property
    def description(self) -> str:
        return "Validates text length against word count constraints"

    def evaluate(self, text: str, **kwargs: Any) -> EvaluatorResult:
        """
        Evaluate word count compliance.

        Args:
            text: Text to evaluate
            max_words: Maximum allowed words (required)
            min_words: Minimum required words (optional, default 0)

        Returns:
            EvaluatorResult with compliance score
        """
        max_words = kwargs.get("max_words")
        min_words = kwargs.get("min_words", 0)

        if max_words is None:
            return EvaluatorResult(
                name=self.name,
                passed=True,
                score=1.0,
                details={"error": "max_words not specified, skipping check"},
            )

        # Count words
        words = text.split()
        word_count = len(words)

        # Check bounds
        within_max = word_count <= max_words
        within_min = word_count >= min_words
        passed = within_max and within_min

        # Calculate score (partial credit for being close)
        if passed:
            score = 1.0
        elif not within_max:
            # Penalty for exceeding max
            excess_ratio = word_count / max_words
            score = max(0.0, 1.0 - (excess_ratio - 1.0))
        else:
            # Penalty for being under min
            if min_words > 0:
                score = word_count / min_words
            else:
                score = 1.0

        return EvaluatorResult(
            name=self.name,
            passed=passed,
            score=score,
            details={
                "word_count": word_count,
                "max_words": max_words,
                "min_words": min_words,
                "within_max": within_max,
                "within_min": within_min,
            },
        )
