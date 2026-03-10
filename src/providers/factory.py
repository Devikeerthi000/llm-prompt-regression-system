"""Factory for creating LLM providers."""

from typing import Any

from src.config.settings import Settings, get_settings
from src.core.exceptions import ConfigurationError
from src.providers.base import BaseLLMProvider
from src.providers.groq_provider import GroqProvider


def create_provider(
    provider: str | None = None,
    settings: Settings | None = None,
    **kwargs: Any,
) -> BaseLLMProvider:
    """
    Factory function to create an LLM provider instance.

    Args:
        provider: Provider name ('groq', 'openai', 'anthropic'). 
                  If None, uses settings default.
        settings: Application settings. If None, loads from environment.
        **kwargs: Additional provider-specific configuration

    Returns:
        Configured LLM provider instance

    Raises:
        ConfigurationError: If provider is not supported or not configured
    """
    if settings is None:
        settings = get_settings()

    provider_name = provider or settings.llm.provider

    # Get API key
    api_key = settings.get_api_key(provider_name)
    if not api_key:
        raise ConfigurationError(
            f"API key not configured for provider: {provider_name}",
            details={
                "provider": provider_name,
                "env_var": f"{provider_name.upper()}_API_KEY",
            },
        )

    # Build provider kwargs
    provider_kwargs = {
        "api_key": api_key,
        "model": kwargs.get("model", settings.llm.model),
        "temperature": kwargs.get("temperature", settings.llm.temperature),
        "max_tokens": kwargs.get("max_tokens", settings.llm.max_tokens),
        "timeout": kwargs.get("timeout", settings.llm.timeout),
        "max_retries": kwargs.get("max_retries", settings.llm.max_retries),
    }

    # Create provider
    providers = {
        "groq": GroqProvider,
        # Future: "openai": OpenAIProvider,
        # Future: "anthropic": AnthropicProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class is None:
        raise ConfigurationError(
            f"Unsupported LLM provider: {provider_name}",
            details={
                "provider": provider_name,
                "supported": list(providers.keys()),
            },
        )

    return provider_class(**provider_kwargs)
