"""Composite evaluator that combines multiple evaluators."""

from typing import Any

from src.evaluators.base import BaseEvaluator, EvaluatorResult
from src.models.schemas import EvaluationResult


class CompositeEvaluator(BaseEvaluator):
    """
    Combines multiple evaluators into a single evaluation pipeline.
    
    Runs all evaluators and aggregates results with weighted scoring.
    """

    def __init__(
        self,
        evaluators: list[BaseEvaluator],
        weight: float = 1.0,
    ) -> None:
        """
        Initialize composite evaluator.

        Args:
            evaluators: List of evaluators to run
            weight: Overall weight for this composite
        """
        super().__init__(weight=weight)
        self._evaluators = evaluators

    @property
    def name(self) -> str:
        return "composite"

    @property
    def description(self) -> str:
        names = [e.name for e in self._evaluators]
        return f"Composite evaluator: {', '.join(names)}"

    @property
    def evaluators(self) -> list[BaseEvaluator]:
        """Return list of evaluators."""
        return self._evaluators

    def add_evaluator(self, evaluator: BaseEvaluator) -> None:
        """Add an evaluator to the pipeline."""
        self._evaluators.append(evaluator)

    def remove_evaluator(self, name: str) -> bool:
        """Remove an evaluator by name."""
        for i, evaluator in enumerate(self._evaluators):
            if evaluator.name == name:
                self._evaluators.pop(i)
                return True
        return False

    def evaluate(self, text: str, **kwargs: Any) -> EvaluatorResult:
        """
        Run all evaluators and aggregate results.

        Args:
            text: Text to evaluate
            **kwargs: Parameters passed to all evaluators

        Returns:
            Aggregated EvaluatorResult
        """
        results: list[EvaluatorResult] = []
        total_weighted_score = 0.0
        total_weight = 0.0

        for evaluator in self._evaluators:
            result = evaluator.evaluate(text, **kwargs)
            results.append(result)
            total_weighted_score += result.score * evaluator.weight
            total_weight += evaluator.weight

        # Calculate weighted average
        avg_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        all_passed = all(r.passed for r in results)

        return EvaluatorResult(
            name=self.name,
            passed=all_passed,
            score=avg_score,
            details={
                "individual_results": [
                    {
                        "name": r.name,
                        "passed": r.passed,
                        "score": r.score,
                        "details": r.details,
                    }
                    for r in results
                ],
                "evaluator_count": len(results),
                "passed_count": sum(1 for r in results if r.passed),
            },
        )

    def evaluate_detailed(self, text: str, **kwargs: Any) -> list[EvaluationResult]:
        """
        Run all evaluators and return detailed results.

        Args:
            text: Text to evaluate
            **kwargs: Parameters for evaluators

        Returns:
            List of EvaluationResult for each evaluator
        """
        results: list[EvaluationResult] = []

        for evaluator in self._evaluators:
            eval_result = evaluator.evaluate(text, **kwargs)
            results.append(
                EvaluationResult(
                    check_name=eval_result.name,
                    passed=eval_result.passed,
                    score=eval_result.score,
                    details=eval_result.details,
                )
            )

        return results
