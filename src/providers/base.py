"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Standardized LLM response container."""

    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    raw_response: Any = None

    @property
    def prompt_tokens(self) -> int:
        return self.usage.get("prompt_tokens", 0)

    @property
    def completion_tokens(self) -> int:
        return self.usage.get("completion_tokens", 0)

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Provides a consistent interface for different LLM backends (Groq, OpenAI, etc.)
    allowing easy switching between providers without changing application code.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        ...

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            Standardized LLMResponse object
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"
