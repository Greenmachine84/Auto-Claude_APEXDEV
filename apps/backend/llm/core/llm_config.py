"""LLM configuration management.

Part of Phase 2: LLM Architecture
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Task types for model selection."""

    CODING = "coding"
    REVIEW = "review"
    PLANNING = "planning"
    CHAT = "chat"
    ANALYSIS = "analysis"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    TESTING = "testing"


@dataclass
class ProviderCredentials:
    """Credentials for an LLM provider."""

    api_key: str | None = None
    api_base: str | None = None
    organization: str | None = None
    project: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls, prefix: str) -> "ProviderCredentials":
        """Load credentials from environment variables."""
        return cls(
            api_key=os.getenv(f"{prefix}_API_KEY"),
            api_base=os.getenv(f"{prefix}_API_BASE"),
            organization=os.getenv(f"{prefix}_ORG"),
            project=os.getenv(f"{prefix}_PROJECT"),
        )


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    requests_per_minute: int = 60
    tokens_per_minute: int = 100000
    concurrent_requests: int = 10


@dataclass
class RetryConfig:
    """Retry policy configuration."""

    max_retries: int = 3
    initial_delay_ms: int = 1000
    max_delay_ms: int = 30000
    exponential_base: float = 2.0
    retryable_errors: list[str] = field(
        default_factory=lambda: ["rate_limit", "timeout", "server_error"]
    )


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    provider: str
    max_tokens: int = 4096
    temperature: float = 0.7
    context_window: int = 8192
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False


class LLMConfig:
    """Central LLM configuration management.

    Manages:
    - Provider credentials
    - Default models per task type
    - Rate limits
    - Retry policies
    """

    _instance: Optional["LLMConfig"] = None

    def __new__(cls) -> "LLMConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._credentials: dict[str, ProviderCredentials] = {}
        self._models: dict[str, ModelConfig] = {}
        self._default_models: dict[TaskType, str] = {}
        self._rate_limits: dict[str, RateLimitConfig] = {}
        self._retry_config = RetryConfig()

        self._load_defaults()
        self._initialized = True

    def _load_defaults(self) -> None:
        """Load default configuration."""
        # Load credentials from environment
        providers = [
            "ANTHROPIC",
            "OPENAI",
            "AZURE",
            "OLLAMA",
            "GEMINI",
            "OPENROUTER",
            "LMSTUDIO",
        ]
        for p in providers:
            self._credentials[p.lower()] = ProviderCredentials.from_env(p)

        # Default rate limits
        self._rate_limits["default"] = RateLimitConfig()

    def get_credentials(self, provider: str) -> ProviderCredentials:
        """Get credentials for a provider."""
        return self._credentials.get(provider.lower(), ProviderCredentials())

    def set_credentials(self, provider: str, creds: ProviderCredentials) -> None:
        """Set credentials for a provider."""
        self._credentials[provider.lower()] = creds

    def get_model(self, name: str) -> ModelConfig | None:
        """Get model configuration."""
        return self._models.get(name)

    def register_model(self, config: ModelConfig) -> None:
        """Register a model configuration."""
        self._models[config.name] = config

    def get_default_model(self, task_type: TaskType) -> str | None:
        """Get default model for a task type."""
        return self._default_models.get(task_type)

    def set_default_model(self, task_type: TaskType, model: str) -> None:
        """Set default model for a task type."""
        self._default_models[task_type] = model

    def get_rate_limit(self, provider: str) -> RateLimitConfig:
        """Get rate limit config for a provider."""
        return self._rate_limits.get(provider.lower(), self._rate_limits["default"])

    def set_rate_limit(self, provider: str, config: RateLimitConfig) -> None:
        """Set rate limit config for a provider."""
        self._rate_limits[provider.lower()] = config

    @property
    def retry_config(self) -> RetryConfig:
        return self._retry_config

    @retry_config.setter
    def retry_config(self, config: RetryConfig) -> None:
        self._retry_config = config

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance."""
        cls._instance = None
