"""LLM Providers module.

Implements 8 canonical LLM providers:
- Copilot (GitHub Copilot)
- OpenRouter
- Ollama (local)
- LM Studio (local)
- Gemini (Google)
- OpenAI
- Anthropic
- Azure OpenAI

Part of Phase 2: LLM Architecture
"""

from .anthropic_provider import AnthropicProvider
from .azure_provider import AzureOpenAIProvider
from .base import BaseLLMProvider, ProviderCapabilities
from .copilot_provider import CopilotProvider
from .gemini_provider import GeminiProvider
from .lmstudio_provider import LMStudioProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider

__all__ = [
    "BaseLLMProvider",
    "ProviderCapabilities",
    "CopilotProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "LMStudioProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "AzureOpenAIProvider",
]
