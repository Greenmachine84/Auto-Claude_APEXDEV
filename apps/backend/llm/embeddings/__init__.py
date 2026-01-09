"""LLM Embeddings module.

Implements 6 embedding providers:
- OpenAI
- Ollama
- Voyage
- Gemini
- Azure OpenAI
- OpenRouter

Part of Phase 2: LLM Architecture
"""

from .azure_embedder import AzureOpenAIEmbedder
from .base import BaseEmbedder, EmbeddingResult
from .gemini_embedder import GeminiEmbedder
from .ollama_embedder import OllamaEmbedder
from .openai_embedder import OpenAIEmbedder
from .openrouter_embedder import OpenRouterEmbedder
from .voyage_embedder import VoyageEmbedder

__all__ = [
    "BaseEmbedder",
    "EmbeddingResult",
    "OpenAIEmbedder",
    "OllamaEmbedder",
    "VoyageEmbedder",
    "GeminiEmbedder",
    "AzureOpenAIEmbedder",
    "OpenRouterEmbedder",
]
