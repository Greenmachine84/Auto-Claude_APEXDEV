"""Azure OpenAI embeddings provider.

Part of Phase 2: LLM Architecture
"""

import logging
import aiohttp
from typing import List
from datetime import datetime

from .base import BaseEmbedder, EmbedderConfig, EmbeddingResult

logger = logging.getLogger(__name__)


class AzureOpenAIEmbedder(BaseEmbedder):
    """Azure OpenAI embeddings API."""
    
    API_VERSION = "2024-02-15-preview"
    
    def __init__(self, config: EmbedderConfig):
        super().__init__(config)
        self._base_url = config.base_url  # Required: Azure endpoint
    
    @property
    def provider_name(self) -> str:
        return "azure"
    
    @property
    def default_model(self) -> str:
        return "text-embedding-ada-002"
    
    @property
    def default_dimensions(self) -> int:
        return 1536
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        start = datetime.utcnow()
        deployment = self._config.model or self.default_model
        
        payload = {"input": texts}
        
        try:
            url = f"{self._base_url}/openai/deployments/{deployment}/embeddings?api-version={self.API_VERSION}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "api-key": self._config.api_key
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
                model=deployment,
                provider=self.provider_name,
                dimensions=len(embeddings[0]) if embeddings else self.default_dimensions,
                usage_tokens=usage.get("total_tokens", 0),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error("Azure OpenAI embedding failed: %s", e)
            raise
