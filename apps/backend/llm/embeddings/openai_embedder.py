"""OpenAI embeddings provider.

Part of Phase 2: LLM Architecture
"""

import logging
import aiohttp
from typing import List
from datetime import datetime

from .base import BaseEmbedder, EmbedderConfig, EmbeddingResult

logger = logging.getLogger(__name__)


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embeddings API."""
    
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, config: EmbedderConfig):
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def default_model(self) -> str:
        return "text-embedding-3-small"
    
    @property
    def default_dimensions(self) -> int:
        return 1536
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        start = datetime.utcnow()
        model = self._config.model or self.default_model
        
        payload = {"input": texts, "model": model}
        if self._config.dimensions:
            payload["dimensions"] = self._config.dimensions
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/embeddings",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._config.api_key}"
                    },
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
                ) as resp:
                    data = await resp.json()
            
            embeddings = [item["embedding"] for item in data.get("data", [])]
            usage = data.get("usage", {})
            
            self._request_count += 1
            self._total_tokens += usage.get("total_tokens", 0)
            
            return EmbeddingResult(
                embeddings=embeddings,
                model=model,
                provider=self.provider_name,
                dimensions=len(embeddings[0]) if embeddings else self.default_dimensions,
                usage_tokens=usage.get("total_tokens", 0),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error("OpenAI embedding failed: %s", e)
            raise
