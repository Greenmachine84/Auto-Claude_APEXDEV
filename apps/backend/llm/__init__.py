"""LLM Module - Multi-Provider LLM Integration.

Phase 2: Memory System & LLM Integration

Provides LLM-agnostic interface supporting 8 canonical providers:
- Copilot (GitHub Copilot)
- OpenRouter
- Ollama (local)
- LM Studio (local)  
- Gemini (Google)
- OpenAI
- Anthropic
- Azure OpenAI

Key features:
- No default provider (explicit configuration required)
- Provider-agnostic routing
- Automatic fallback handling
- Cost tracking and metrics
- Streaming support
- Tool calling framework

Submodules:
- core: Central LLM management, routing, fallback
- providers: 8 LLM provider implementations
- embeddings: Embedding providers
- prompts: Prompt templating and registry
- streaming: Stream handling and parsing
- tools: Tool calling framework
- types: Type definitions
"""

from .core import (
    LLMManager,
    ProviderRegistry,
    LLMRouter,
    RouteResult,
    FallbackHandler,
    FallbackResult,
    LLMMetrics,
    MetricEvent,
)
from .providers import (
    BaseLLMProvider,
    ProviderCapabilities,
    CopilotProvider,
    OpenRouterProvider,
    OllamaProvider,
    LMStudioProvider,
    GeminiProvider,
    OpenAIProvider,
    AnthropicProvider,
    AzureOpenAIProvider,
)
from .types import (
    LLMCapability,
    LLMModel,
    LLMUsage,
    ModelInfo,
    ProviderType,
    ProviderStatus,
    ProviderConfig,
    LLMResponse,
    StreamChunk,
    ToolCall,
    ToolResult,
    LLMConfig,
    RouterConfig,
    FallbackConfig,
)

__all__ = [
    # Core
    "LLMManager",
    "ProviderRegistry",
    "LLMRouter",
    "RouteResult",
    "FallbackHandler",
    "FallbackResult",
    "LLMMetrics",
    "MetricEvent",
    # Providers
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
    # Types
    "LLMCapability",
    "LLMModel",
    "LLMUsage",
    "ModelInfo",
    "ProviderType",
    "ProviderStatus",
    "ProviderConfig",
    "LLMResponse",
    "StreamChunk",
    "ToolCall",
    "ToolResult",
    "LLMConfig",
    "RouterConfig",
    "FallbackConfig",
]
