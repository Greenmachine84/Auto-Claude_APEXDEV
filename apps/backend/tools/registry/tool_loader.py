"""
Tool Loader - Phase 8 Implementation.

Dynamic tool loading from modules and files.

World-Class Standards:
- Hot reload capability
- Validation on load
- Error recovery
- Plugin architecture
"""

from typing import Dict, Any, Optional, List, Type
from pathlib import Path
import importlib
import importlib.util
import inspect
import logging
import sys

from ..models import Tool, ToolCategory, ToolParameter, ParameterType
from .tool_registry import ToolRegistry
from .tool_validator import ToolValidator

logger = logging.getLogger(__name__)


class ToolLoader:
    """
    Dynamic tool loader with hot reload support.
    
    Features:
    - Module-based loading
    - File-based loading
    - Validation on load
    - Dependency tracking
    """
    
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        validator: Optional[ToolValidator] = None,
    ) -> None:
        """Initialize loader."""
        self.registry = registry or ToolRegistry()
        self.validator = validator or ToolValidator()
        
        # Track loaded modules for hot reload
        self._loaded_modules: Dict[str, str] = {}  # path -> module name
        
        logger.info("ToolLoader initialized")
    
    async def load_from_module(
        self,
        module_path: str,
        prefix: str = "",
    ) -> List[str]:
        """
        Load tools from a Python module.
        
        Args:
            module_path: Dotted module path (e.g., "tools.builtin.file_tools")
            prefix: Optional prefix for tool names
            
        Returns:
            List of loaded tool names
        """
        loaded = []
        
        try:
            module = importlib.import_module(module_path)
            
            # Look for tool definitions
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Tool):
                    tool = obj
                    if prefix:
                        tool.name = f"{prefix}_{tool.name}"
                    
                    # Validate
                    valid, errors = self.validator.validate(tool)
                    if not valid:
                        logger.error(
                            "Invalid tool %s: %s", tool.name, errors
                        )
                        continue
                    
                    # Register
                    await self.registry.register(tool, registered_by="loader")
                    loaded.append(tool.name)
                
                elif inspect.isfunction(obj) and hasattr(obj, "_tool_definition"):
                    # Function decorated as tool
                    tool = self._function_to_tool(obj)
                    if prefix:
                        tool.name = f"{prefix}_{tool.name}"
                    
                    valid, errors = self.validator.validate(tool)
                    if not valid:
                        logger.error(
                            "Invalid tool %s: %s", tool.name, errors
                        )
                        continue
                    
                    await self.registry.register(tool, registered_by="loader")
                    loaded.append(tool.name)
            
            self._loaded_modules[module_path] = module.__name__
            logger.info("Loaded %d tools from %s", len(loaded), module_path)
            
        except Exception as e:
            logger.error("Failed to load module %s: %s", module_path, e)
            raise
        
        return loaded
    
    async def load_from_file(
        self,
        file_path: str,
        prefix: str = "",
    ) -> List[str]:
        """
        Load tools from a Python file.
        
        Args:
            file_path: Path to Python file
            prefix: Optional prefix for tool names
            
        Returns:
            List of loaded tool names
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Tool file not found: {file_path}")
        
        if not path.suffix == ".py":
            raise ValueError("Tool file must be a Python file")
        
        loaded = []
        
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(
                path.stem, str(path)
            )
            if not spec or not spec.loader:
                raise ImportError(f"Cannot load module from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            # Look for tools
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Tool):
                    tool = obj
                    if prefix:
                        tool.name = f"{prefix}_{tool.name}"
                    
                    valid, errors = self.validator.validate(tool)
                    if valid:
                        await self.registry.register(tool, registered_by="loader")
                        loaded.append(tool.name)
            
            self._loaded_modules[file_path] = spec.name
            logger.info("Loaded %d tools from %s", len(loaded), file_path)
            
        except Exception as e:
            logger.error("Failed to load file %s: %s", file_path, e)
            raise
        
        return loaded
    
    async def load_from_directory(
        self,
        directory: str,
        prefix: str = "",
        recursive: bool = True,
    ) -> List[str]:
        """
        Load all tools from a directory.
        
        Args:
            directory: Directory path
            prefix: Optional prefix for tool names
            recursive: Whether to search subdirectories
            
        Returns:
            List of loaded tool names
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        loaded = []
        pattern = "**/*.py" if recursive else "*.py"
        
        for file_path in dir_path.glob(pattern):
            if file_path.name.startswith("_"):
                continue
            
            try:
                file_loaded = await self.load_from_file(str(file_path), prefix)
                loaded.extend(file_loaded)
            except Exception as e:
                logger.warning("Skipping %s: %s", file_path, e)
        
        return loaded
    
    async def reload_module(self, module_path: str) -> List[str]:
        """
        Hot reload a previously loaded module.
        
        Args:
            module_path: Module path to reload
            
        Returns:
            List of reloaded tool names
        """
        if module_path not in self._loaded_modules:
            raise ValueError(f"Module {module_path} was not loaded")
        
        module_name = self._loaded_modules[module_path]
        
        # Get current tools from this module
        old_tools = []
        for name, reg in list(self.registry._tools.items()):
            if hasattr(reg.tool, "_source_module") and reg.tool._source_module == module_name:
                old_tools.append(name)
        
        # Unregister old tools
        for name in old_tools:
            await self.registry.unregister(name)
        
        # Reload module
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Load again
        return await self.load_from_module(module_path)
    
    def _function_to_tool(self, func) -> Tool:
        """Convert a decorated function to a Tool."""
        tool_def = func._tool_definition
        
        # Extract parameters from function signature
        sig = inspect.signature(func)
        parameters = []
        
        for name, param in sig.parameters.items():
            if name in ("context", "self"):
                continue
            
            param_type = ParameterType.STRING
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = ParameterType.INTEGER
                elif param.annotation == float:
                    param_type = ParameterType.FLOAT
                elif param.annotation == bool:
                    param_type = ParameterType.BOOLEAN
                elif param.annotation == list:
                    param_type = ParameterType.ARRAY
                elif param.annotation == dict:
                    param_type = ParameterType.OBJECT
            
            parameters.append(ToolParameter(
                name=name,
                type=param_type,
                description=tool_def.get("params", {}).get(name, {}).get(
                    "description", f"Parameter {name}"
                ),
                required=param.default == inspect.Parameter.empty,
                default=param.default if param.default != inspect.Parameter.empty else None,
            ))
        
        return Tool(
            name=tool_def.get("name", func.__name__),
            description=tool_def.get("description", func.__doc__ or ""),
            category=tool_def.get("category", ToolCategory.UTILITY),
            parameters=parameters,
            handler=func,
            tags=tool_def.get("tags", []),
        )


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: ToolCategory = ToolCategory.UTILITY,
    tags: Optional[List[str]] = None,
    params: Optional[Dict[str, Dict[str, str]]] = None,
):
    """
    Decorator for defining tools from functions.
    
    Usage:
        @tool(name="my_tool", description="Does something")
        async def my_tool(context, arg1: str, arg2: int = 0):
            return result
    """
    def decorator(func):
        func._tool_definition = {
            "name": name or func.__name__,
            "description": description or func.__doc__ or "",
            "category": category,
            "tags": tags or [],
            "params": params or {},
        }
        return func
    return decorator
