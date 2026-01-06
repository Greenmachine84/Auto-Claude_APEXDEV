"""Execution context for orchestrated tasks.

Provides context and utilities for task execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from orchestrator.core.config import OrchestratorConfig


logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Context for task execution.
    
    Provides access to:
    - Task metadata
    - Configuration
    - Logging
    - State management
    - Resource tracking
    
    Example:
        context = ExecutionContext(task_id="task_1")
        context.log("Starting execution")
        context.set_state("phase", "processing")
    """
    
    task_id: str
    config: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    
    # Execution metadata
    started_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    
    # State management
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    steps: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def log(self, message: str, level: str = "info") -> None:
        """Log a message."""
        log_func = getattr(logger, level, logger.info)
        log_func(f"[{self.task_id}] {message}")
        
        self.steps.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        })
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        self.state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        return self.state.get(key, default)
    
    def add_error(self, error: str) -> None:
        """Add an error."""
        self.errors.append(error)
        self.log(error, level="error")
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return (datetime.now() - self.started_at).total_seconds()
    
    def is_timeout(self) -> bool:
        """Check if execution has timed out."""
        return self.get_elapsed_time() > self.config.task_timeout
    
    def create_child_context(self, child_task_id: str) -> "ExecutionContext":
        """Create a child context."""
        return ExecutionContext(
            task_id=child_task_id,
            config=self.config,
            parent_id=self.task_id,
            workflow_id=self.workflow_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "started_at": self.started_at.isoformat(),
            "elapsed_seconds": self.get_elapsed_time(),
            "parent_id": self.parent_id,
            "workflow_id": self.workflow_id,
            "state": self.state,
            "metadata": self.metadata,
            "steps": self.steps,
            "errors": self.errors,
        }


@dataclass
class ResourceTracker:
    """Track resource usage during execution."""
    
    context: ExecutionContext
    memory_bytes: int = 0
    cpu_percent: float = 0.0
    api_calls: int = 0
    tokens_used: int = 0
    
    def track_memory(self, bytes_used: int) -> None:
        """Track memory usage."""
        self.memory_bytes = max(self.memory_bytes, bytes_used)
    
    def track_api_call(self, tokens: int = 0) -> None:
        """Track API call."""
        self.api_calls += 1
        self.tokens_used += tokens
    
    def check_limits(self) -> bool:
        """Check if within resource limits."""
        config = self.context.config
        
        if self.memory_bytes > config.max_memory_mb * 1024 * 1024:
            return False
        if self.cpu_percent > config.max_cpu_percent:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_bytes": self.memory_bytes,
            "cpu_percent": self.cpu_percent,
            "api_calls": self.api_calls,
            "tokens_used": self.tokens_used,
        }
