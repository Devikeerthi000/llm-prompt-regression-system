"""Groq LLM provider implementation."""

import time
from typing import Any

from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.exceptions import LLMProviderError
from src.core.logging import get_logger
from src.providers.base import BaseLLMProvider, LLMResponse

logger = get_logger(__name__)


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM provider for fast inference.
    
    Supports Llama, Mixtral, and other models available on Groq Cloud.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._api_key = api_key
        self._client: Groq | None = None

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def client(self) -> Groq:
        """Lazy initialization of Groq client."""
        if self._client is None:
            self._client = Groq(api_key=self._api_key)
        return self._client

    def is_available(self) -> bool:
        """Check if Groq provider is available."""
        return bool(self._api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """
        Generate a response using Groq's API.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated content

        Raises:
            LLMProviderError: If generation fails
        """
        if not self.is_available():
            raise LLMProviderError(
                "Groq API key not configured",
                details={"provider": self.provider_name},
            )

        # Override defaults with kwargs
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        logger.debug(f"Generating response with model={self.model}")
        start_time = time.perf_counter()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            content = response.choices[0].message.content or ""

            logger.debug(
                f"Generated response: {len(content)} chars, "
                f"{usage.get('total_tokens', 0)} tokens, {latency_ms:.2f}ms"
            )

            return LLMResponse(
                content=content.strip(),
                model=self.model,
                provider=self.provider_name,
                usage=usage,
                latency_ms=latency_ms,
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise LLMProviderError(
                f"Failed to generate response: {e}",
                details={
                    "provider": self.provider_name,
                    "model": self.model,
                    "error_type": type(e).__name__,
                },
            ) from e
