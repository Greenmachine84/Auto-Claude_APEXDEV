"""
Tools Registry Tests - Phase 8.

Tests for tool models, registry, loader, discovery, and validation.
Focus on module importability and basic class instantiation.
"""

import pytest


class TestToolModelsImport:
    """Test tool models are importable."""

    def test_import_tool(self):
        """Test importing Tool class."""
        from apps.backend.tools.models import Tool
        assert Tool is not None

    def test_import_tool_category(self):
        """Test importing ToolCategory enum."""
        from apps.backend.tools.models import ToolCategory
        assert ToolCategory is not None
        # Verify expected categories exist
        assert hasattr(ToolCategory, 'FILE')
        assert hasattr(ToolCategory, 'WEB')
        assert hasattr(ToolCategory, 'GIT')

    def test_import_tool_status(self):
        """Test importing ToolStatus enum."""
        from apps.backend.tools.models import ToolStatus
        assert ToolStatus is not None
        # Use actual enum values: FAILURE not FAILED
        assert hasattr(ToolStatus, 'SUCCESS')
        assert hasattr(ToolStatus, 'FAILURE')

    def test_import_tool_parameter(self):
        """Test importing ToolParameter."""
        from apps.backend.tools.models import ToolParameter
        assert ToolParameter is not None

    def test_import_parameter_type(self):
        """Test importing ParameterType."""
        from apps.backend.tools.models import ParameterType
        assert ParameterType is not None

    def test_import_tool_result(self):
        """Test importing ToolResult."""
        from apps.backend.tools.models import ToolResult
        assert ToolResult is not None


class TestToolCreation:
    """Test creating Tool instances."""

    def test_create_simple_tool(self):
        """Test creating a simple tool."""
        from apps.backend.tools.models import Tool, ToolCategory
        
        tool = Tool(
            name="test_tool",
            description="A test tool for unit testing",
            category=ToolCategory.UTILITY,
            parameters=[],
        )
        assert tool.name == "test_tool"
        assert tool.category == ToolCategory.UTILITY

    def test_tool_with_parameter(self):
        """Test creating a tool with parameters."""
        from apps.backend.tools.models import Tool, ToolCategory, ToolParameter, ParameterType
        
        param = ToolParameter(
            name="input_path",
            type=ParameterType.STRING,
            description="Path to input file",
            required=True,
        )
        tool = Tool(
            name="file_reader",
            description="Reads a file",
            category=ToolCategory.FILE,
            parameters=[param],
        )
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "input_path"


class TestToolRegistryImport:
    """Test ToolRegistry is importable."""

    def test_import_registry(self):
        """Test importing ToolRegistry."""
        from apps.backend.tools.registry.tool_registry import ToolRegistry
        assert ToolRegistry is not None

    def test_instantiate_registry(self):
        """Test creating ToolRegistry instance."""
        from apps.backend.tools.registry.tool_registry import ToolRegistry
        registry = ToolRegistry()
        assert registry is not None

    def test_registry_has_register_method(self):
        """Test registry has register method."""
        from apps.backend.tools.registry.tool_registry import ToolRegistry
        registry = ToolRegistry()
        assert hasattr(registry, 'register') or hasattr(registry, 'register_tool')


class TestToolValidatorImport:
    """Test ToolValidator is importable."""

    def test_import_validator(self):
        """Test importing ToolValidator."""
        from apps.backend.tools.registry.tool_validator import ToolValidator
        assert ToolValidator is not None

    def test_instantiate_validator(self):
        """Test creating ToolValidator instance."""
        from apps.backend.tools.registry.tool_validator import ToolValidator
        validator = ToolValidator()
        assert validator is not None


class TestToolLoaderImport:
    """Test ToolLoader is importable."""

    def test_import_loader(self):
        """Test importing ToolLoader."""
        from apps.backend.tools.registry.tool_loader import ToolLoader
        assert ToolLoader is not None

    def test_instantiate_loader(self):
        """Test creating ToolLoader instance."""
        from apps.backend.tools.registry.tool_loader import ToolLoader
        loader = ToolLoader()
        assert loader is not None


class TestToolDiscoveryImport:
    """Test ToolDiscovery is importable."""

    def test_import_discovery(self):
        """Test importing ToolDiscovery."""
        from apps.backend.tools.registry.tool_discovery import ToolDiscovery
        assert ToolDiscovery is not None

    def test_instantiate_discovery(self):
        """Test creating ToolDiscovery instance."""
        from apps.backend.tools.registry.tool_discovery import ToolDiscovery
        discovery = ToolDiscovery()
        assert discovery is not None
