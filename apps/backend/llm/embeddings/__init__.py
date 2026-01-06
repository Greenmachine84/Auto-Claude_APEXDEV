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

from .base import BaseEmbedder, EmbeddingResult
from .openai_embedder import OpenAIEmbedder
from .ollama_embedder import OllamaEmbedder
from .voyage_embedder import VoyageEmbedder
from .gemini_embedder import GeminiEmbedder
from .azure_embedder import AzureOpenAIEmbedder
from .openrouter_embedder import OpenRouterEmbedder

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
