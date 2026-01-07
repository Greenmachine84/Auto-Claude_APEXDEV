"""
Enhanced Tool Registry - Phase 8 Implementation.

Central registry for tool management with lifecycle support.

World-Class Standards:
- Thread-safe registration
- Hot reload capability
- Version management
- Category organization
"""

from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import threading

from ..models import Tool, ToolCategory, ToolParameter, ToolStatus

logger = logging.getLogger(__name__)


@dataclass
class ToolRegistration:
    """Registration record for a tool."""
    tool: Tool
    registered_at: str
    registered_by: str
    version: str
    enabled: bool = True
    usage_count: int = 0
    last_used_at: Optional[str] = None


class ToolRegistry:
    """
    Central tool registry with lifecycle management.
    
    Features:
    - Thread-safe registration
    - Category-based organization
    - Version tracking
    - Enable/disable support
    """
    
    _instance: Optional["ToolRegistry"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "ToolRegistry":
        """Singleton pattern for registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize registry."""
        if self._initialized:
            return
        
        self._tools: Dict[str, ToolRegistration] = {}
        self._by_category: Dict[ToolCategory, List[str]] = {}
        self._callbacks: List[Callable] = []
        self._async_lock = asyncio.Lock()
        
        self._initialized = True
        logger.info("ToolRegistry initialized")
    
    async def register(
        self,
        tool: Tool,
        registered_by: str = "system",
    ) -> bool:
        """
        Register a tool.
        
        Args:
            tool: Tool to register
            registered_by: Registrant identifier
            
        Returns:
            True if registered successfully
        """
        async with self._async_lock:
            if tool.name in self._tools:
                existing = self._tools[tool.name]
                if existing.version == tool.version:
                    logger.warning("Tool %s already registered", tool.name)
                    return False
                
                # Update existing registration
                logger.info("Updating tool %s to version %s", tool.name, tool.version)
            
            registration = ToolRegistration(
                tool=tool,
                registered_at=datetime.utcnow().isoformat(),
                registered_by=registered_by,
                version=tool.version,
                enabled=tool.enabled,
            )
            
            self._tools[tool.name] = registration
            
            # Update category index
            if tool.category not in self._by_category:
                self._by_category[tool.category] = []
            if tool.name not in self._by_category[tool.category]:
                self._by_category[tool.category].append(tool.name)
            
            logger.info("Registered tool: %s v%s", tool.name, tool.version)
            
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback("register", tool.name)
                except Exception as e:
                    logger.error("Callback error: %s", e)
            
            return True
    
    async def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        async with self._async_lock:
            if name not in self._tools:
                return False
            
            registration = self._tools.pop(name)
            
            # Update category index
            category = registration.tool.category
            if category in self._by_category:
                if name in self._by_category[category]:
                    self._by_category[category].remove(name)
            
            logger.info("Unregistered tool: %s", name)
            return True
    
    async def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        async with self._async_lock:
            registration = self._tools.get(name)
            if registration and registration.enabled:
                return registration.tool
            return None
    
    async def get_all(self) -> List[Tool]:
        """Get all registered tools."""
        async with self._async_lock:
            return [
                reg.tool for reg in self._tools.values()
                if reg.enabled
            ]
    
    async def get_by_category(self, category: ToolCategory) -> List[Tool]:
        """Get tools by category."""
        async with self._async_lock:
            names = self._by_category.get(category, [])
            tools = []
            for name in names:
                reg = self._tools.get(name)
                if reg and reg.enabled:
                    tools.append(reg.tool)
            return tools
    
    async def get_by_tags(self, tags: List[str]) -> List[Tool]:
        """Get tools matching any of the tags."""
        async with self._async_lock:
            matching = []
            for reg in self._tools.values():
                if reg.enabled and any(tag in reg.tool.tags for tag in tags):
                    matching.append(reg.tool)
            return matching
    
    async def enable(self, name: str) -> bool:
        """Enable a tool."""
        async with self._async_lock:
            if name in self._tools:
                self._tools[name].enabled = True
                return True
            return False
    
    async def disable(self, name: str) -> bool:
        """Disable a tool."""
        async with self._async_lock:
            if name in self._tools:
                self._tools[name].enabled = False
                return True
            return False
    
    async def record_usage(self, name: str) -> None:
        """Record tool usage."""
        async with self._async_lock:
            if name in self._tools:
                self._tools[name].usage_count += 1
                self._tools[name].last_used_at = datetime.utcnow().isoformat()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        async with self._async_lock:
            total = len(self._tools)
            enabled = sum(1 for r in self._tools.values() if r.enabled)
            by_category = {
                cat.value: len(names)
                for cat, names in self._by_category.items()
            }
            
            top_used = sorted(
                self._tools.values(),
                key=lambda r: r.usage_count,
                reverse=True,
            )[:10]
            
            return {
                "total_tools": total,
                "enabled_tools": enabled,
                "disabled_tools": total - enabled,
                "by_category": by_category,
                "top_used": [
                    {"name": r.tool.name, "count": r.usage_count}
                    for r in top_used
                ],
            }
    
    def add_callback(self, callback: Callable) -> None:
        """Add registration callback."""
        self._callbacks.append(callback)
    
    async def clear(self) -> None:
        """Clear all registrations."""
        async with self._async_lock:
            self._tools.clear()
            self._by_category.clear()
        logger.info("Registry cleared")
    
    def to_openai_functions(self) -> List[Dict[str, Any]]:
        """Export all tools as OpenAI function definitions."""
        return [
            reg.tool.to_openai_function()
            for reg in self._tools.values()
            if reg.enabled
        ]
    
    def to_anthropic_tools(self) -> List[Dict[str, Any]]:
        """Export all tools as Anthropic tool definitions."""
        return [
            reg.tool.to_anthropic_tool()
            for reg in self._tools.values()
            if reg.enabled
        ]
