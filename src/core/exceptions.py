"""Custom exceptions for PromptGuard AI."""

from typing import Any


class PromptGuardError(Exception):
    """Base exception for all PromptGuard errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(PromptGuardError):
    """Raised when there's a configuration issue."""

    pass


class LLMProviderError(PromptGuardError):
    """Raised when LLM provider encounters an error."""

    pass


class EvaluationError(PromptGuardError):
    """Raised when evaluation fails."""

    pass


class DataLoadError(PromptGuardError):
    """Raised when data loading fails."""

    pass


class ValidationError(PromptGuardError):
    """Raised when data validation fails."""

    pass
