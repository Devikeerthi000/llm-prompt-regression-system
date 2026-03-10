"""Abstract base class for evaluators."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluatorResult:
    """Result from an evaluator."""

    name: str
    passed: bool
    score: float  # Normalized 0-1
    details: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        # Ensure score is normalized
        self.score = max(0.0, min(1.0, self.score))


class BaseEvaluator(ABC):
    """
    Abstract base class for output evaluators.

    Evaluators inspect LLM outputs against specific criteria and return
    a normalized score with detailed results.
    """

    def __init__(self, weight: float = 1.0) -> None:
        """
        Initialize evaluator with optional weight.

        Args:
            weight: Importance weight for this evaluator (default 1.0)
        """
        self.weight = weight

    @property
    @abstractmethod
    def name(self) -> str:
        """Return evaluator name."""
        ...

    @property
    def description(self) -> str:
        """Return evaluator description."""
        return f"{self.name} evaluator"

    @abstractmethod
    def evaluate(self, text: str, **kwargs: Any) -> EvaluatorResult:
        """
        Evaluate the given text.

        Args:
            text: Text to evaluate
            **kwargs: Additional evaluation parameters

        Returns:
            EvaluatorResult with score and details
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(weight={self.weight})"
