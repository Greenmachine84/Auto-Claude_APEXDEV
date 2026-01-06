"""Tool registry.

Central registry for tool discovery and management.

Capabilities:
- Register tools
- Discover tools by category
- Get tool by name
- List all tools
"""

from typing import Dict, List, Optional, Type, Set
import threading

from tools.core.base_tool import BaseTool, ToolCategory


class ToolRegistry:
    """Central registry for all tools.
    
    Thread-safe singleton registry for tool management.
    
    Example:
        registry = ToolRegistry()
        registry.register(MyTool)
        
        tool = registry.get("my_tool")
        fs_tools = registry.get_by_category(ToolCategory.FILESYSTEM)
    """
    
    _instance: Optional["ToolRegistry"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "ToolRegistry":
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize registry."""
        if self._initialized:
            return
        
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        self._categories: Dict[ToolCategory, Set[str]] = {
            cat: set() for cat in ToolCategory
        }
        self._initialized = True
    
    def register(self, tool_class: Type[BaseTool]) -> None:
        """Register a tool class.
        
        Args:
            tool_class: Tool class to register
        """
        with self._lock:
            name = tool_class.name
            if name in self._tool_classes:
                raise ValueError(f"Tool already registered: {name}")
            
            self._tool_classes[name] = tool_class
            self._categories[tool_class.category].add(name)
    
    def register_instance(self, tool: BaseTool) -> None:
        """Register a tool instance.
        
        Args:
            tool: Tool instance to register
        """
        with self._lock:
            name = tool.name
            if name in self._tools:
                raise ValueError(f"Tool instance already registered: {name}")
            
            self._tools[name] = tool
            self._tool_classes[name] = type(tool)
            self._categories[tool.category].add(name)
    
    def unregister(self, name: str) -> None:
        """Unregister a tool.
        
        Args:
            name: Name of tool to unregister
        """
        with self._lock:
            if name in self._tools:
                tool = self._tools[name]
                self._categories[tool.category].discard(name)
                del self._tools[name]
            
            if name in self._tool_classes:
                tool_class = self._tool_classes[name]
                self._categories[tool_class.category].discard(name)
                del self._tool_classes[name]
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None
        """
        # Return existing instance
        if name in self._tools:
            return self._tools[name]
        
        # Create instance from class
        if name in self._tool_classes:
            tool = self._tool_classes[name]()
            self._tools[name] = tool
            return tool
        
        return None
    
    def get_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """Get all tools in a category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tools
        """
        tools = []
        for name in self._categories.get(category, set()):
            tool = self.get(name)
            if tool:
                tools.append(tool)
        return tools
    
    def list_all(self) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tool_classes.keys())
    
    def list_by_category(self) -> Dict[str, List[str]]:
        """List tools grouped by category.
        
        Returns:
            Dictionary of category to tool names
        """
        return {
            cat.value: list(names)
            for cat, names in self._categories.items()
            if names
        }
    
    def get_schema(self, name: str) -> Optional[Dict]:
        """Get JSON schema for a tool.
        
        Args:
            name: Tool name
            
        Returns:
            Tool schema or None
        """
        tool = self.get(name)
        if tool:
            return tool.get_schema()
        return None
    
    def get_all_schemas(self) -> List[Dict]:
        """Get schemas for all tools.
        
        Returns:
            List of tool schemas
        """
        return [
            tool.get_schema()
            for name in self._tool_classes
            if (tool := self.get(name))
        ]
    
    def clear(self) -> None:
        """Clear all registered tools."""
        with self._lock:
            self._tools.clear()
            self._tool_classes.clear()
            for cat in self._categories:
                self._categories[cat].clear()
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tool_classes)
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tool_classes
