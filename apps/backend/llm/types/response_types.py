"""Response type definitions.

Part of Phase 2: LLM Architecture
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .llm_types import LLMUsage


class FinishReason(Enum):
    """Reason for response completion."""

    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


@dataclass
class ToolCall:
    """A tool call requested by the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]
    type: str = "function"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "function": {"name": self.name, "arguments": self.arguments},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolCall":
        func = data.get("function", {})
        return cls(
            id=data.get("id", ""),
            name=func.get("name", ""),
            arguments=func.get("arguments", {}),
            type=data.get("type", "function"),
        )


@dataclass
class ToolResult:
    """Result from executing a tool."""

    tool_call_id: str
    content: str
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_call_id": self.tool_call_id,
            "content": self.content,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""

    content: str = ""
    delta: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: FinishReason | None = None
    index: int = 0

    @property
    def is_final(self) -> bool:
        return self.finish_reason is not None


@dataclass
class LLMResponse:
    """Complete response from an LLM call."""

    id: str
    model: str
    provider: str
    content: str
    role: str = "assistant"
    finish_reason: FinishReason = FinishReason.STOP
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: LLMUsage = field(default_factory=LLMUsage)
    created_at: datetime = field(default_factory=datetime.utcnow)
    latency_ms: float = 0.0
    cached: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "model": self.model,
            "provider": self.provider,
            "content": self.content,
            "role": self.role,
            "finish_reason": self.finish_reason.value,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "usage": self.usage.to_dict(),
            "created_at": self.created_at.isoformat(),
            "latency_ms": self.latency_ms,
            "cached": self.cached,
        }

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0
