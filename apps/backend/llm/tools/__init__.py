"""LLM Tools module.

Provides tool/function calling infrastructure:
- Tool schema for JSON Schema definitions
- Tool registry for registration and lookup
- Tool executor for execution engine
- Tool result handling

Part of Phase 2: LLM Architecture
"""

from .tool_schema import (
    ToolSchema,
    ToolParameter,
    ParameterType,
    create_tool_schema,
)
from .tool_registry import ToolRegistry
from .tool_executor import ToolExecutor, ExecutionContext
from .tool_result import ToolResult, ToolError, ResultType

__all__ = [
    "ToolSchema",
    "ToolParameter",
    "ParameterType",
    "create_tool_schema",
    "ToolRegistry",
    "ToolExecutor",
    "ExecutionContext",
    "ToolResult",
    "ToolError",
    "ResultType",
]
