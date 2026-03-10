"""Evaluator registry for managing and creating evaluators."""

from typing import Type

from src.evaluators.base import BaseEvaluator
from src.evaluators.word_count import WordCountEvaluator
from src.evaluators.hashtag import HashtagEvaluator
from src.evaluators.tone import ToneEvaluator
from src.evaluators.composite import CompositeEvaluator
from src.providers.base import BaseLLMProvider


class EvaluatorRegistry:
    """
    Registry for managing evaluator types.
    
    Provides factory methods for creating evaluators by name.
    """

    _evaluators: dict[str, Type[BaseEvaluator]] = {}

    @classmethod
    def register(cls, name: str, evaluator_class: Type[BaseEvaluator]) -> None:
        """Register an evaluator class."""
        cls._evaluators[name.lower()] = evaluator_class

    @classmethod
    def get(cls, name: str) -> Type[BaseEvaluator] | None:
        """Get an evaluator class by name."""
        return cls._evaluators.get(name.lower())

    @classmethod
    def list_evaluators(cls) -> list[str]:
        """List all registered evaluator names."""
        return list(cls._evaluators.keys())

    @classmethod
    def create(cls, name: str, **kwargs) -> BaseEvaluator:
        """
        Create an evaluator instance by name.

        Args:
            name: Evaluator name
            **kwargs: Constructor arguments

        Returns:
            Evaluator instance

        Raises:
            ValueError: If evaluator is not registered
        """
        evaluator_class = cls.get(name)
        if evaluator_class is None:
            raise ValueError(
                f"Unknown evaluator: {name}. "
                f"Available: {', '.join(cls.list_evaluators())}"
            )
        return evaluator_class(**kwargs)


# Register built-in evaluators
EvaluatorRegistry.register("word_count", WordCountEvaluator)
EvaluatorRegistry.register("hashtags", HashtagEvaluator)


def get_default_evaluators(llm_provider: BaseLLMProvider) -> CompositeEvaluator:
    """
    Create the default evaluator pipeline.

    Args:
        llm_provider: LLM provider for evaluators that need it

    Returns:
        CompositeEvaluator with all default evaluators
    """
    return CompositeEvaluator(
        evaluators=[
            WordCountEvaluator(weight=1.0),
            HashtagEvaluator(weight=1.0),
            ToneEvaluator(llm_provider=llm_provider, weight=1.0),
        ]
    )
