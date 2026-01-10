"""Provider type definitions.

Part of Phase 2: LLM Architecture
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProviderType(Enum):
    """Canonical LLM provider types."""

    COPILOT = "copilot"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class ProviderStatus(Enum):
    """Health status of a provider."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    AUTH_ERROR = "auth_error"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Health information for a provider."""

    status: ProviderStatus
    latency_ms: float = 0.0
    last_check: datetime = field(default_factory=datetime.utcnow)
    error_rate: float = 0.0
    consecutive_failures: int = 0
    message: str = ""


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""

    provider_type: ProviderType
    api_key: str | None = None
    base_url: str | None = None
    api_version: str | None = None
    organization: str | None = None
    project: str | None = None
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    rate_limit_rpm: int = 0  # 0 = no limit
    rate_limit_tpm: int = 0  # 0 = no limit
    headers: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0  # Higher = preferred

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_type": self.provider_type.value,
            "base_url": self.base_url,
            "api_version": self.api_version,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "rate_limit_rpm": self.rate_limit_rpm,
            "enabled": self.enabled,
            "priority": self.priority,
        }

    @classmethod
    def for_copilot(cls) -> "ProviderConfig":
        return cls(provider_type=ProviderType.COPILOT)

    @classmethod
    def for_openai(cls, api_key: str) -> "ProviderConfig":
        return cls(
            provider_type=ProviderType.OPENAI,
            api_key=api_key,
            base_url="https://api.openai.com/v1",
        )

    @classmethod
    def for_anthropic(cls, api_key: str) -> "ProviderConfig":
        return cls(
            provider_type=ProviderType.ANTHROPIC,
            api_key=api_key,
            base_url="https://api.anthropic.com",
        )

    @classmethod
    def for_ollama(cls, base_url: str = "http://localhost:11434") -> "ProviderConfig":
        return cls(provider_type=ProviderType.OLLAMA, base_url=base_url)

    @classmethod
    def for_lmstudio(
        cls, base_url: str = "http://localhost:1234/v1"
    ) -> "ProviderConfig":
        return cls(provider_type=ProviderType.LMSTUDIO, base_url=base_url)
