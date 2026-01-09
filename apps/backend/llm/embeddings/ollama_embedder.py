"""Ollama embeddings provider.

Part of Phase 2: LLM Architecture
"""

import logging
from datetime import datetime

import aiohttp

from .base import BaseEmbedder, EmbedderConfig, EmbeddingResult

logger = logging.getLogger(__name__)


class OllamaEmbedder(BaseEmbedder):
    """Ollama local embeddings."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: EmbedderConfig):
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return "nomic-embed-text"

    @property
    def default_dimensions(self) -> int:
        return 768

    async def embed(self, texts: list[str]) -> EmbeddingResult:
        start = datetime.utcnow()
        model = self._config.model or self.default_model
        embeddings = []

        try:
            async with aiohttp.ClientSession() as session:
                for text in texts:
                    async with session.post(
                        f"{self._base_url}/api/embeddings",
                        json={"model": model, "prompt": text},
                        timeout=aiohttp.ClientTimeout(
                            total=self._config.timeout_seconds
                        ),
                    ) as resp:
                        data = await resp.json()
                        embeddings.append(data.get("embedding", []))

            self._request_count += len(texts)

            return EmbeddingResult(
                embeddings=embeddings,
                model=model,
                provider=self.provider_name,
                dimensions=len(embeddings[0])
                if embeddings
                else self.default_dimensions,
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000,
            )

        except Exception as e:
            logger.error("Ollama embedding failed: %s", e)
            raise
