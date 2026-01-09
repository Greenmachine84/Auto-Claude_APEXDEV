"""Base embedder abstraction.

Part of Phase 2: LLM Architecture
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""

    embeddings: list[list[float]]
    model: str
    provider: str
    dimensions: int
    usage_tokens: int = 0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def first(self) -> list[float]:
        return self.embeddings[0] if self.embeddings else []

    def to_dict(self) -> dict[str, Any]:
        return {
            "embeddings": self.embeddings,
            "model": self.model,
            "provider": self.provider,
            "dimensions": self.dimensions,
            "usage_tokens": self.usage_tokens,
            "latency_ms": self.latency_ms,
        }


@dataclass
class EmbedderConfig:
    """Configuration for an embedder."""

    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    dimensions: int | None = None
    batch_size: int = 100
    timeout_seconds: int = 60
    max_retries: int = 3


class BaseEmbedder(ABC):
    """Abstract base class for embedding providers."""

    def __init__(self, config: EmbedderConfig):
        self._config = config
        self._request_count = 0
        self._total_tokens = 0

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    @property
    @abstractmethod
    def default_dimensions(self) -> int:
        pass

    @abstractmethod
    async def embed(self, texts: list[str]) -> EmbeddingResult:
        """Embed a list of texts."""
        pass

    async def embed_single(self, text: str) -> list[float]:
        """Embed a single text."""
        result = await self.embed([text])
        return result.first

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed texts in batches."""
        all_embeddings = []
        batch_size = self._config.batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            result = await self.embed(batch)
            all_embeddings.extend(result.embeddings)

        return all_embeddings
