"""Tool result handling.

Part of Phase 2: LLM Architecture
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ResultType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ToolError(Exception):
    """Error during tool execution."""
    
    def __init__(self, message: str, code: str = "UNKNOWN", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass
class ToolResult:
    """Result of a tool execution."""
    tool_call_id: str
    tool_name: str
    result: Any = None
    error: Optional[str] = None
    result_type: ResultType = ResultType.SUCCESS
    error_code: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.result_type == ResultType.SUCCESS
    
    @property
    def has_error(self) -> bool:
        """Check if there was an error."""
        return self.error is not None
    
    def to_message(self) -> str:
        """Convert to message string for LLM."""
        if self.success:
            if isinstance(self.result, str):
                return self.result
            return json.dumps(self.result, default=str)
        return f"Error: {self.error}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_call_id": self.tool_call_id,
            "tool_name": self.tool_name,
            "result": self.result,
            "error": self.error,
            "result_type": self.result_type.value,
            "error_code": self.error_code,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata
        }
    
    def to_openai_message(self) -> Dict[str, Any]:
        """Convert to OpenAI tool message format."""
        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "content": self.to_message()
        }
    
    def to_anthropic_block(self) -> Dict[str, Any]:
        """Convert to Anthropic tool_result block."""
        block = {
            "type": "tool_result",
            "tool_use_id": self.tool_call_id,
            "content": self.to_message()
        }
        if self.has_error:
            block["is_error"] = True
        return block


@dataclass
class ToolResultBatch:
    """Batch of tool results."""
    results: List[ToolResult] = field(default_factory=list)
    
    @property
    def all_success(self) -> bool:
        """Check if all executions were successful."""
        return all(r.success for r in self.results)
    
    @property
    def has_errors(self) -> bool:
        """Check if any execution had errors."""
        return any(r.has_error for r in self.results)
    
    @property
    def total_duration_ms(self) -> float:
        """Get total duration."""
        return sum(r.duration_ms for r in self.results)
    
    def get_errors(self) -> List[ToolResult]:
        """Get results with errors."""
        return [r for r in self.results if r.has_error]
    
    def get_successful(self) -> List[ToolResult]:
        """Get successful results."""
        return [r for r in self.results if r.success]
    
    def to_openai_messages(self) -> List[Dict[str, Any]]:
        """Convert all to OpenAI messages."""
        return [r.to_openai_message() for r in self.results]
    
    def to_anthropic_blocks(self) -> List[Dict[str, Any]]:
        """Convert all to Anthropic blocks."""
        return [r.to_anthropic_block() for r in self.results]
    
    def add(self, result: ToolResult) -> None:
        """Add a result."""
        self.results.append(result)
    
    def merge(self, other: "ToolResultBatch") -> "ToolResultBatch":
        """Merge with another batch."""
        return ToolResultBatch(results=self.results + other.results)
