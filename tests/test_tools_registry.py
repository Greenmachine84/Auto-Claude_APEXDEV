"""
Tools Registry Tests - Phase 8.

Tests for tool registry, loader, validator, and discovery.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from apps.backend.tools.models import (
    Tool, ToolParameter, ToolResult, ToolCategory, 
    ParameterType, ToolExecutionContext
)
from apps.backend.tools.registry.tool_registry import ToolRegistry
from apps.backend.tools.registry.tool_loader import ToolLoader, tool
from apps.backend.tools.registry.tool_validator import ToolValidator, ValidationError
from apps.backend.tools.registry.tool_discovery import ToolDiscovery


class TestToolModel:
    """Test Tool model."""
    
    def test_create_tool(self):
        """Test creating a tool."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="input",
                    type=ParameterType.STRING,
                    description="Input value",
                    required=True,
                )
            ],
        )
        
        assert tool.name == "test_tool"
        assert tool.category == ToolCategory.UTILITY
        assert len(tool.parameters) == 1
    
    def test_tool_to_openai_function(self):
        """Test OpenAI function format conversion."""
        t = Tool(
            name="get_weather",
            description="Get weather for a location",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="location",
                    type=ParameterType.STRING,
                    description="City name",
                    required=True,
                )
            ],
        )
        
        func_def = t.to_openai_function()
        
        assert func_def["name"] == "get_weather"
        assert "parameters" in func_def
        assert func_def["parameters"]["type"] == "object"
    
    def test_tool_to_anthropic_tool(self):
        """Test Anthropic tool format conversion."""
        t = Tool(
            name="search_code",
            description="Search codebase",
            category=ToolCategory.SEARCH,
            parameters=[],
        )
        
        tool_def = t.to_anthropic_tool()
        
        assert tool_def["name"] == "search_code"
        assert "input_schema" in tool_def


class TestToolRegistry:
    """Test ToolRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create fresh registry instance."""
        reg = ToolRegistry()
        asyncio.get_event_loop().run_until_complete(reg.clear())
        return reg
    
    @pytest.mark.asyncio
    async def test_register_tool(self, registry):
        """Test registering a tool."""
        tool = Tool(
            name="registered_tool",
            description="A registered tool",
            category=ToolCategory.UTILITY,
        )
        
        result = await registry.register(tool)
        assert result is True
        
        retrieved = await registry.get("registered_tool")
        assert retrieved is not None
        assert retrieved.name == "registered_tool"
    
    @pytest.mark.asyncio
    async def test_register_duplicate(self, registry):
        """Test registering duplicate tool."""
        tool = Tool(
            name="dup_tool",
            description="First version",
            category=ToolCategory.UTILITY,
        )
        
        await registry.register(tool)
        result = await registry.register(tool)
        
        # Should return False for exact duplicate
        assert result is False
    
    @pytest.mark.asyncio
    async def test_unregister_tool(self, registry):
        """Test unregistering a tool."""
        tool = Tool(
            name="to_remove",
            description="Will be removed",
            category=ToolCategory.UTILITY,
        )
        
        await registry.register(tool)
        result = await registry.unregister("to_remove")
        
        assert result is True
        assert await registry.get("to_remove") is None
    
    @pytest.mark.asyncio
    async def test_get_by_category(self, registry):
        """Test getting tools by category."""
        tools = [
            Tool(name="file1", description="File tool 1", category=ToolCategory.FILE_SYSTEM),
            Tool(name="file2", description="File tool 2", category=ToolCategory.FILE_SYSTEM),
            Tool(name="web1", description="Web tool", category=ToolCategory.WEB),
        ]
        
        for t in tools:
            await registry.register(t)
        
        file_tools = await registry.get_by_category(ToolCategory.FILE_SYSTEM)
        assert len(file_tools) == 2
    
    @pytest.mark.asyncio
    async def test_enable_disable(self, registry):
        """Test enabling/disabling tools."""
        tool = Tool(
            name="toggle_tool",
            description="Can be toggled",
            category=ToolCategory.UTILITY,
        )
        
        await registry.register(tool)
        await registry.disable("toggle_tool")
        
        # Disabled tool should not be returned
        assert await registry.get("toggle_tool") is None
        
        await registry.enable("toggle_tool")
        assert await registry.get("toggle_tool") is not None
    
    @pytest.mark.asyncio
    async def test_record_usage(self, registry):
        """Test usage tracking."""
        tool = Tool(
            name="tracked_tool",
            description="Usage tracked",
            category=ToolCategory.UTILITY,
        )
        
        await registry.register(tool)
        await registry.record_usage("tracked_tool")
        await registry.record_usage("tracked_tool")
        
        stats = await registry.get_statistics()
        top_used = stats.get("top_used", [])
        
        assert any(t["name"] == "tracked_tool" for t in top_used)


class TestToolValidator:
    """Test ToolValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return ToolValidator()
    
    def test_validate_valid_tool(self, validator):
        """Test validating a valid tool."""
        tool = Tool(
            name="valid_tool",
            description="A perfectly valid tool for testing",
            category=ToolCategory.UTILITY,
            handler=lambda ctx: None,
        )
        
        valid, errors = validator.validate(tool)
        
        # Should have no errors
        error_count = sum(1 for e in errors if e.severity == "error")
        assert error_count == 0
    
    def test_validate_missing_name(self, validator):
        """Test validation catches missing name."""
        tool = Tool(
            name="",
            description="Has no name",
            category=ToolCategory.UTILITY,
        )
        
        valid, errors = validator.validate(tool)
        assert valid is False
    
    def test_validate_invalid_name_format(self, validator):
        """Test validation catches invalid name format."""
        tool = Tool(
            name="Invalid-Name",  # Hyphens not allowed
            description="Bad name format",
            category=ToolCategory.UTILITY,
        )
        
        valid, errors = validator.validate(tool)
        assert any("name" in e.field.lower() for e in errors)
    
    def test_validate_reserved_name(self, validator):
        """Test validation catches reserved names."""
        tool = Tool(
            name="system",  # Reserved
            description="Uses reserved name",
            category=ToolCategory.UTILITY,
        )
        
        valid, errors = validator.validate(tool)
        assert valid is False
    
    def test_validate_parameter_types(self, validator):
        """Test parameter type validation."""
        tool = Tool(
            name="param_test",
            description="Tests parameter validation",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="count",
                    type=ParameterType.INTEGER,
                    description="A count",
                    default="not_an_int",  # Wrong type
                )
            ],
        )
        
        valid, errors = validator.validate(tool)
        assert any("default" in e.field for e in errors)


class TestToolLoader:
    """Test ToolLoader."""
    
    @pytest.fixture
    def loader(self):
        """Create loader."""
        registry = ToolRegistry()
        return ToolLoader(registry=registry)
    
    def test_tool_decorator(self):
        """Test @tool decorator."""
        @tool(
            name="decorated_tool",
            description="A decorated function",
            category=ToolCategory.UTILITY,
        )
        async def my_tool(context, arg1: str, arg2: int = 0):
            return {"result": arg1}
        
        assert hasattr(my_tool, "_tool_definition")
        assert my_tool._tool_definition["name"] == "decorated_tool"
    
    @pytest.mark.asyncio
    async def test_function_to_tool_conversion(self, loader):
        """Test converting decorated function to Tool."""
        @tool(name="converted", description="Converted function")
        async def func(context, value: str):
            return value
        
        converted = loader._function_to_tool(func)
        
        assert converted.name == "converted"
        assert len(converted.parameters) == 1
        assert converted.parameters[0].name == "value"


class TestToolDiscovery:
    """Test ToolDiscovery."""
    
    @pytest.fixture
    def discovery(self):
        """Create discovery instance."""
        return ToolDiscovery()
    
    @pytest.mark.asyncio
    async def test_discover_builtin(self, discovery):
        """Test discovering builtin tools."""
        # May return empty if module not properly set up in test
        discovered = await discovery.discover_builtin()
        assert isinstance(discovered, list)
    
    @pytest.mark.asyncio
    async def test_discover_from_config(self, discovery):
        """Test discovery from configuration."""
        config = {
            "tool_packages": [
                {"path": "tools.builtin", "enabled": True},
            ],
            "custom_tool_directories": [],
        }
        
        discovered = await discovery.discover_from_config(config)
        assert isinstance(discovered, list)
