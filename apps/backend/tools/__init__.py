"""Tools Module.

Provides tools for agent interaction with external systems:
- Core tool infrastructure
- Filesystem operations
- Git operations
- Terminal commands
- Web requests
- Search capabilities

Version: 1.0.0
"""

from tools.core.base_tool import BaseTool, ToolContext, ToolResult
from tools.core.permissions import Permission, PermissionManager
from tools.core.sandbox import Sandbox, SandboxConfig
from tools.core.tool_executor import ToolExecutor
from tools.core.tool_registry import ToolRegistry

__version__ = "1.0.0"

__all__ = [
    # Core
    "BaseTool",
    "ToolContext",
    "ToolResult",
    "ToolRegistry",
    "ToolExecutor",
    "PermissionManager",
    "Permission",
    "Sandbox",
    "SandboxConfig",
]
