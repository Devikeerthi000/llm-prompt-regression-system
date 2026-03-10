"""Tone validation evaluator using LLM."""

from typing import Any

from src.core.exceptions import EvaluationError
from src.core.logging import get_logger
from src.evaluators.base import BaseEvaluator, EvaluatorResult
from src.providers.base import BaseLLMProvider

logger = get_logger(__name__)


class ToneEvaluator(BaseEvaluator):
    """
    Evaluates text tone using LLM-based analysis.
    
    Uses the LLM to assess whether the text matches the expected tone
    (professional, casual, formal, etc.).
    """

    TONE_CHECK_PROMPT = """Analyze the tone of the following text and determine if it matches the expected tone.

Expected tone: {expected_tone}

Text to analyze:
---
{text}
---

Respond with ONLY "YES" if the text matches the expected {expected_tone} tone, or "NO" if it doesn't.
Do not include any other text in your response."""

    def __init__(
        self, 
        llm_provider: BaseLLMProvider,
        weight: float = 1.0,
    ) -> None:
        """
        Initialize tone evaluator with LLM provider.

        Args:
            llm_provider: LLM provider for tone analysis
            weight: Evaluator weight
        """
        super().__init__(weight=weight)
        self.llm_provider = llm_provider

    @property
    def name(self) -> str:
        return "tone"

    @property
    def description(self) -> str:
        return "LLM-based tone validation"

    def evaluate(self, text: str, **kwargs: Any) -> EvaluatorResult:
        """
        Evaluate tone compliance using LLM.

        Args:
            text: Text to evaluate
            tone: Expected tone (e.g., 'professional', 'casual')

        Returns:
            EvaluatorResult with tone analysis
        """
        expected_tone = kwargs.get("tone", "professional")

        if not text.strip():
            return EvaluatorResult(
                name=self.name,
                passed=False,
                score=0.0,
                details={"error": "Empty text provided"},
            )

        try:
            prompt = self.TONE_CHECK_PROMPT.format(
                expected_tone=expected_tone,
                text=text[:2000],  # Limit text length
            )

            response = self.llm_provider.generate(
                prompt,
                temperature=0.0,  # Deterministic for evaluation
                max_tokens=10,
            )

            answer = response.content.strip().upper()
            passed = answer.startswith("YES")

            logger.debug(
                f"Tone check for '{expected_tone}': {answer} "
                f"(latency: {response.latency_ms:.2f}ms)"
            )

            return EvaluatorResult(
                name=self.name,
                passed=passed,
                score=1.0 if passed else 0.0,
                details={
                    "expected_tone": expected_tone,
                    "llm_response": answer,
                    "latency_ms": response.latency_ms,
                },
            )

        except Exception as e:
            logger.warning(f"Tone evaluation failed: {e}")
            raise EvaluationError(
                f"Failed to evaluate tone: {e}",
                details={"expected_tone": expected_tone},
            ) from e
