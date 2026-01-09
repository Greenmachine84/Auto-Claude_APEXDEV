"""Tool registry for registration and lookup.

Part of Phase 2: LLM Architecture
"""

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .tool_schema import ToolSchema, create_tool_schema

logger = logging.getLogger(__name__)


@dataclass
class RegisteredTool:
    """A registered tool with metadata."""

    schema: ToolSchema
    handler: Callable
    category: str = "general"
    enabled: bool = True
    requires_confirmation: bool = False
    rate_limit: int | None = None  # calls per minute
    registered_at: datetime = field(default_factory=datetime.utcnow)
    call_count: int = 0
    last_called: datetime | None = None


class ToolRegistry:
    """Registry for tools/functions."""

    _instance: Optional["ToolRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._tools: dict[str, RegisteredTool] = {}
        self._categories: dict[str, set[str]] = {}  # category -> tool names
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("ToolRegistry initialized")

    def register(
        self,
        handler: Callable,
        schema: ToolSchema | None = None,
        category: str = "general",
        requires_confirmation: bool = False,
        rate_limit: int | None = None,
    ) -> RegisteredTool:
        """Register a tool."""
        if schema is None:
            schema = create_tool_schema(handler)

        with self._lock:
            if schema.name in self._tools:
                logger.warning("Overwriting existing tool: %s", schema.name)

            tool = RegisteredTool(
                schema=schema,
                handler=handler,
                category=category,
                requires_confirmation=requires_confirmation,
                rate_limit=rate_limit,
            )

            self._tools[schema.name] = tool

            if category not in self._categories:
                self._categories[category] = set()
            self._categories[category].add(schema.name)

            logger.info("Registered tool: %s (category=%s)", schema.name, category)
            return tool

    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        with self._lock:
            if name not in self._tools:
                return False

            tool = self._tools.pop(name)
            if tool.category in self._categories:
                self._categories[tool.category].discard(name)

            logger.info("Unregistered tool: %s", name)
            return True

    def get(self, name: str) -> RegisteredTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_handler(self, name: str) -> Callable | None:
        """Get a tool's handler."""
        tool = self.get(name)
        return tool.handler if tool else None

    def list_tools(
        self, category: str | None = None, enabled_only: bool = True
    ) -> list[RegisteredTool]:
        """List registered tools."""
        tools = list(self._tools.values())

        if category:
            tools = [t for t in tools if t.category == category]

        if enabled_only:
            tools = [t for t in tools if t.enabled]

        return tools

    def list_schemas(
        self, category: str | None = None, format: str = "openai"
    ) -> list[dict[str, Any]]:
        """List tool schemas in specified format."""
        tools = self.list_tools(category=category)

        if format == "anthropic":
            return [t.schema.to_anthropic_schema() for t in tools]
        return [t.schema.to_openai_schema() for t in tools]

    def list_categories(self) -> list[str]:
        """List all categories."""
        return list(self._categories.keys())

    def enable(self, name: str) -> bool:
        """Enable a tool."""
        tool = self.get(name)
        if tool:
            tool.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a tool."""
        tool = self.get(name)
        if tool:
            tool.enabled = False
            return True
        return False

    def record_call(self, name: str) -> None:
        """Record a tool call for metrics."""
        tool = self.get(name)
        if tool:
            tool.call_count += 1
            tool.last_called = datetime.utcnow()

    def clear(self) -> None:
        """Clear all registered tools."""
        with self._lock:
            self._tools.clear()
            self._categories.clear()
            logger.info("Cleared all tools")

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance."""
        with cls._lock:
            cls._instance = None


def tool(
    category: str = "general",
    requires_confirmation: bool = False,
    rate_limit: int | None = None,
) -> Callable:
    """Decorator to register a function as a tool."""

    def decorator(func: Callable) -> Callable:
        ToolRegistry().register(
            handler=func,
            category=category,
            requires_confirmation=requires_confirmation,
            rate_limit=rate_limit,
        )
        return func

    return decorator
