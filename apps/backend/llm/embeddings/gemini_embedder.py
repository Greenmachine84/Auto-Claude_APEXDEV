"""Google Gemini embeddings provider.

Part of Phase 2: LLM Architecture
"""

import logging
import aiohttp
from typing import List
from datetime import datetime

from .base import BaseEmbedder, EmbedderConfig, EmbeddingResult

logger = logging.getLogger(__name__)


class GeminiEmbedder(BaseEmbedder):
    """Google Gemini embeddings API."""
    
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, config: EmbedderConfig):
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    @property
    def default_model(self) -> str:
        return "text-embedding-004"
    
    @property
    def default_dimensions(self) -> int:
        return 768
    
    async def embed(self, texts: List[str]) -> EmbeddingResult:
        start = datetime.utcnow()
        model = self._config.model or self.default_model
        embeddings = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for text in texts:
                    url = f"{self._base_url}/models/{model}:embedContent?key={self._config.api_key}"
                    payload = {"content": {"parts": [{"text": text}]}}
                    
                    async with session.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
                    ) as resp:
                        data = await resp.json()
                        embedding = data.get("embedding", {}).get("values", [])
                        embeddings.append(embedding)
            
            self._request_count += len(texts)
            
            return EmbeddingResult(
                embeddings=embeddings,
                model=model,
                provider=self.provider_name,
                dimensions=len(embeddings[0]) if embeddings else self.default_dimensions,
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error("Gemini embedding failed: %s", e)
            raise
