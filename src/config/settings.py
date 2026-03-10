"""Application settings using Pydantic Settings management."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderSettings(BaseSettings):
    """LLM Provider configuration."""

    provider: Literal["groq", "openai", "anthropic"] = Field(
        default="groq",
        description="LLM provider to use",
    )
    model: str = Field(
        default="llama-3.1-8b-instant",
        description="Model identifier",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(
        default=1024,
        gt=0,
        description="Maximum tokens in response",
    )
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts",
    )


class EvaluationSettings(BaseSettings):
    """Evaluation configuration."""

    pass_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum score to pass evaluation",
    )
    regression_threshold: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Score drop that indicates regression",
    )
    parallel_execution: bool = Field(
        default=False,
        description="Execute test cases in parallel",
    )
    max_workers: int = Field(
        default=4,
        gt=0,
        description="Max parallel workers",
    )


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="PromptGuard AI")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Paths
    data_dir: Path = Field(
        default=Path("data"),
        description="Data directory path",
    )
    output_dir: Path = Field(
        default=Path("outputs"),
        description="Output directory path",
    )
    log_dir: Path = Field(
        default=Path("logs"),
        description="Log directory path",
    )

    # API Keys (using SecretStr for security)
    groq_api_key: SecretStr | None = Field(
        default=None,
        description="Groq API key",
    )
    openai_api_key: SecretStr | None = Field(
        default=None,
        description="OpenAI API key",
    )
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        description="Anthropic API key",
    )

    # Nested settings
    llm: LLMProviderSettings = Field(default_factory=LLMProviderSettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)

    @field_validator("data_dir", "output_dir", "log_dir", mode="after")
    @classmethod
    def ensure_directory_exists(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_api_key(self, provider: str) -> str | None:
        """Get API key for the specified provider."""
        key_map = {
            "groq": self.groq_api_key,
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
        }
        secret = key_map.get(provider.lower())
        return secret.get_secret_value() if secret else None


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
