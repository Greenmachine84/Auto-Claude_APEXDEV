"""
Tool Models - Phase 8 Implementation.

Core data models for the tool framework.

World-Class Standards:
- Type-safe definitions
- Comprehensive validation
- Serialization support
- Extensible design
"""

from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class ToolCategory(Enum):
    """Tool categories for organization."""
    FILE = "file"
    WEB = "web"
    GIT = "git"
    SEARCH = "search"
    SHELL = "shell"
    DATABASE = "database"
    API = "api"
    UTILITY = "utility"
    CUSTOM = "custom"


class ToolStatus(Enum):
    """Tool execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ParameterType(Enum):
    """Tool parameter types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FILE_PATH = "file_path"
    URL = "url"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None  # Allowed values
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None  # Regex pattern for strings
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """Validate a value against this parameter definition."""
        if value is None:
            if self.required and self.default is None:
                return False, f"Parameter '{self.name}' is required"
            return True, ""
        
        # Type validation
        if self.type == ParameterType.STRING:
            if not isinstance(value, str):
                return False, f"Parameter '{self.name}' must be a string"
        elif self.type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False, f"Parameter '{self.name}' must be an integer"
        elif self.type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)):
                return False, f"Parameter '{self.name}' must be a number"
        elif self.type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"Parameter '{self.name}' must be a boolean"
        elif self.type == ParameterType.ARRAY:
            if not isinstance(value, list):
                return False, f"Parameter '{self.name}' must be an array"
        elif self.type == ParameterType.OBJECT:
            if not isinstance(value, dict):
                return False, f"Parameter '{self.name}' must be an object"
        
        # Enum validation
        if self.enum and value not in self.enum:
            return False, f"Parameter '{self.name}' must be one of: {self.enum}"
        
        # Range validation
        if self.min_value is not None and value < self.min_value:
            return False, f"Parameter '{self.name}' must be >= {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"Parameter '{self.name}' must be <= {self.max_value}"
        
        return True, ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "enum": self.enum,
        }


@dataclass
class ToolResult:
    """Result of a tool execution."""
    tool_name: str
    status: ToolStatus
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    started_at: str = ""
    completed_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ToolStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }


@dataclass
class ToolExecutionContext:
    """Context for tool execution."""
    user_id: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    working_directory: str = "."
    environment: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    allow_network: bool = True
    allow_file_write: bool = True
    allow_shell: bool = False  # Disabled by default for security
    max_output_size: int = 1024 * 1024  # 1MB
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def with_timeout(self, seconds: float) -> "ToolExecutionContext":
        """Create a copy with different timeout."""
        return ToolExecutionContext(
            user_id=self.user_id,
            agent_id=self.agent_id,
            session_id=self.session_id,
            working_directory=self.working_directory,
            environment=self.environment.copy(),
            timeout_seconds=seconds,
            allow_network=self.allow_network,
            allow_file_write=self.allow_file_write,
            allow_shell=self.allow_shell,
            max_output_size=self.max_output_size,
            metadata=self.metadata.copy(),
        )


@dataclass
class Tool:
    """Tool definition with execution handler."""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    handler: Optional[Callable] = None  # Async function
    version: str = "1.0.0"
    enabled: bool = True
    requires_confirmation: bool = False
    tags: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate tool definition."""
        if not self.name:
            raise ValueError("Tool name is required")
        if not self.description:
            raise ValueError("Tool description is required")
    
    def get_parameter(self, name: str) -> Optional[ToolParameter]:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate input parameters."""
        errors = []
        
        for param in self.parameters:
            value = inputs.get(param.name, param.default)
            valid, error = param.validate(value)
            if not valid:
                errors.append(error)
        
        # Check for unknown parameters
        known_params = {p.name for p in self.parameters}
        for key in inputs:
            if key not in known_params:
                errors.append(f"Unknown parameter: {key}")
        
        return len(errors) == 0, errors
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type.value if param.type != ParameterType.FILE_PATH else "string",
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
    
    def to_anthropic_tool(self) -> Dict[str, Any]:
        """Convert to Anthropic tool format."""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        
        for param in self.parameters:
            input_schema["properties"][param.name] = {
                "type": param.type.value if param.type != ParameterType.FILE_PATH else "string",
                "description": param.description,
            }
            if param.required:
                input_schema["required"].append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": input_schema,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": [p.to_dict() for p in self.parameters],
            "version": self.version,
            "enabled": self.enabled,
            "requires_confirmation": self.requires_confirmation,
            "tags": self.tags,
            "examples": self.examples,
        }


@dataclass
class ToolExecution:
    """Record of a tool execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ToolExecutionContext] = None
    result: Optional[ToolResult] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
