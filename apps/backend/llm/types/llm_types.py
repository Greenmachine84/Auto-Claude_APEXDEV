"""Core LLM type definitions.

Part of Phase 2: LLM Architecture
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Flag, auto


class LLMCapability(Flag):
    """Capabilities supported by LLM providers."""
    CHAT = auto()
    COMPLETION = auto()
    EMBEDDING = auto()
    VISION = auto()
    FUNCTION_CALLING = auto()
    TOOL_USE = auto()
    STREAMING = auto()
    JSON_MODE = auto()
    SYSTEM_PROMPT = auto()
    STRUCTURED_OUTPUT = auto()
    
    @classmethod
    def full(cls) -> "LLMCapability":
        return cls.CHAT | cls.STREAMING | cls.FUNCTION_CALLING | cls.TOOL_USE | cls.JSON_MODE | cls.SYSTEM_PROMPT


@dataclass
class ModelInfo:
    """Information about an LLM model."""
    id: str
    name: str
    provider: str
    context_length: int
    max_output_tokens: int
    capabilities: LLMCapability
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_vision: bool = False
    supports_tools: bool = False
    deprecated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "provider": self.provider,
            "context_length": self.context_length, "max_output_tokens": self.max_output_tokens,
            "capabilities": self.capabilities.value, "cost_per_1k_input": self.cost_per_1k_input,
            "cost_per_1k_output": self.cost_per_1k_output, "supports_vision": self.supports_vision,
            "supports_tools": self.supports_tools, "deprecated": self.deprecated
        }


@dataclass
class LLMModel:
    """A configured LLM model instance."""
    info: ModelInfo
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: Optional[int] = None
    stop_sequences: List[str] = field(default_factory=list)
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.info.id, "temperature": self.temperature,
            "top_p": self.top_p, "max_tokens": self.max_tokens,
            "stop": self.stop_sequences, "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty
        }


@dataclass
class LLMUsage:
    """Token usage for an LLM call."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    
    @property
    def cost(self) -> float:
        # Base cost calculation, provider-specific overrides
        return 0.0
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens, "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens, "cached_tokens": self.cached_tokens
        }
