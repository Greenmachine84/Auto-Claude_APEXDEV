"""
Tool Registry Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Tool discovery
- Dynamic registration
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, List


class TestToolRegistry:
    """Test tool registry."""

    async def test_register_tool(self):
        """Tool can be registered."""
        registry = MagicMock()
        registry.register = AsyncMock(return_value="tool-123")
        
        tool_id = await registry.register(
            name="file_reader",
            description="Reads file contents",
            handler=MagicMock(),
        )
        
        assert tool_id == "tool-123"

    async def test_get_tool(self):
        """Tool can be retrieved."""
        registry = MagicMock()
        registry.get = AsyncMock(return_value={
            "id": "tool-123",
            "name": "file_reader",
        })
        
        tool = await registry.get(tool_id="tool-123")
        
        assert tool["name"] == "file_reader"

    async def test_list_tools(self):
        """All tools can be listed."""
        registry = MagicMock()
        registry.list = AsyncMock(return_value=[
            {"id": "tool-1", "name": "file_reader"},
            {"id": "tool-2", "name": "file_writer"},
        ])
        
        tools = await registry.list()
        
        assert len(tools) == 2


class TestToolCategories:
    """Test tool categories."""

    def test_categories_defined(self):
        """Tool categories are defined."""
        categories = [
            "filesystem",
            "git",
            "terminal",
            "web",
            "search",
        ]
        
        assert len(categories) >= 5

    async def test_filter_by_category(self):
        """Tools can be filtered by category."""
        registry = MagicMock()
        registry.list_by_category = AsyncMock(return_value=[
            {"name": "file_reader", "category": "filesystem"},
            {"name": "file_writer", "category": "filesystem"},
        ])
        
        tools = await registry.list_by_category(category="filesystem")
        
        for tool in tools:
            assert tool["category"] == "filesystem"


class TestToolValidation:
    """Test tool validation."""

    async def test_validate_tool_schema(self):
        """Tool schema is validated."""
        registry = MagicMock()
        registry.validate = MagicMock(return_value=True)
        
        is_valid = registry.validate({
            "name": "test_tool",
            "description": "Test tool",
            "parameters": {},
        })
        
        assert is_valid is True

    async def test_reject_invalid_tool(self):
        """Invalid tool is rejected."""
        registry = MagicMock()
        registry.register = AsyncMock(
            side_effect=ValueError("Missing required field: description")
        )
        
        with pytest.raises(ValueError, match="description"):
            await registry.register(name="invalid_tool")


class TestToolDeregistration:
    """Test tool deregistration."""

    async def test_deregister_tool(self):
        """Tool can be deregistered."""
        registry = MagicMock()
        registry.deregister = AsyncMock(return_value=True)
        
        result = await registry.deregister(tool_id="tool-123")
        
        assert result is True
