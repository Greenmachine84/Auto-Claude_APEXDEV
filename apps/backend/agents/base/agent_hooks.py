"""Agent Lifecycle Hooks.

Defines APEX Constitution lifecycle hooks for agents.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Hooks provide extension points for:
- Pre/post execution
- Error handling
- Memory operations
- State transitions
"""

import functools
import logging
from enum import Enum, auto
from typing import Any, Callable, TypeVar, ParamSpec
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class HookType(Enum):
    """Types of lifecycle hooks."""

    PRE_EXECUTE = auto()
    POST_EXECUTE = auto()
    ON_ERROR = auto()
    ON_RETRY = auto()
    ON_TIMEOUT = auto()
    PRE_TOOL_CALL = auto()
    POST_TOOL_CALL = auto()
    ON_MEMORY_STORE = auto()
    ON_MEMORY_RECALL = auto()
    ON_STATE_CHANGE = auto()
    ON_TASK_START = auto()
    ON_TASK_COMPLETE = auto()
    ON_SPAWN_AGENT = auto()


@dataclass
class HookContext:
    """Context passed to hooks."""

    hook_type: HookType
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Exception | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


HookCallable = Callable[[HookContext], None]
AsyncHookCallable = Callable[[HookContext], Any]  # For async hooks


class AgentHooks:
    """Registry and executor for agent lifecycle hooks.

    Manages hook registration and execution for APEX Constitution compliance.
    Supports both sync and async hooks.

    Usage:
        >>> hooks = AgentHooks(agent_id="coder-001")
        >>> @hooks.register(HookType.PRE_EXECUTE)
        ... def log_execution(ctx: HookContext):
        ...     print(f"Starting execution at {ctx.timestamp}")
    """

    def __init__(self, agent_id: str):
        """Initialize hooks registry.

        Args:
            agent_id: Agent identifier for logging
        """
        self.agent_id = agent_id
        self._hooks: dict[HookType, list[HookCallable]] = {
            hook_type: [] for hook_type in HookType
        }
        self._enabled = True

    @property
    def enabled(self) -> bool:
        """Check if hooks are enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable hook execution."""
        self._enabled = True

    def disable(self) -> None:
        """Disable hook execution."""
        self._enabled = False

    def register(
        self, hook_type: HookType
    ) -> Callable[[HookCallable], HookCallable]:
        """Decorator to register a hook.

        Args:
            hook_type: Type of hook to register

        Returns:
            Decorator function
        """
        def decorator(func: HookCallable) -> HookCallable:
            self._hooks[hook_type].append(func)
            return func
        return decorator

    def add_hook(self, hook_type: HookType, hook: HookCallable) -> None:
        """Add a hook programmatically.

        Args:
            hook_type: Type of hook
            hook: Hook function
        """
        self._hooks[hook_type].append(hook)

    def remove_hook(self, hook_type: HookType, hook: HookCallable) -> bool:
        """Remove a hook.

        Args:
            hook_type: Type of hook
            hook: Hook function to remove

        Returns:
            True if hook was found and removed
        """
        if hook in self._hooks[hook_type]:
            self._hooks[hook_type].remove(hook)
            return True
        return False

    def clear_hooks(self, hook_type: HookType | None = None) -> None:
        """Clear hooks.

        Args:
            hook_type: Specific hook type to clear, or None for all
        """
        if hook_type:
            self._hooks[hook_type] = []
        else:
            for ht in HookType:
                self._hooks[ht] = []

    def execute(
        self,
        hook_type: HookType,
        *,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        result: Any = None,
        error: Exception | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Execute all hooks of a given type.

        Args:
            hook_type: Type of hooks to execute
            args: Arguments from original call
            kwargs: Keyword arguments from original call
            result: Result from execution (for post hooks)
            error: Error from execution (for error hooks)
            metadata: Additional metadata
        """
        if not self._enabled:
            return

        context = HookContext(
            hook_type=hook_type,
            agent_id=self.agent_id,
            args=args,
            kwargs=kwargs or {},
            result=result,
            error=error,
            metadata=metadata or {},
        )

        for hook in self._hooks[hook_type]:
            try:
                hook(context)
            except Exception as e:
                logger.error(
                    f"Hook error ({hook_type.name} in {self.agent_id}): {e}"
                )

    def get_hooks(self, hook_type: HookType) -> list[HookCallable]:
        """Get all hooks of a type.

        Args:
            hook_type: Type of hooks to get

        Returns:
            List of hook functions
        """
        return list(self._hooks[hook_type])


# Convenience decorators for common hooks

def hook(hook_type: HookType) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Mark a method as a hook handler.

    Usage:
        >>> class MyAgent(BaseAgent):
        ...     @hook(HookType.PRE_EXECUTE)
        ...     def prepare(self, ctx: HookContext):
        ...         self.logger.info("Preparing execution")
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        func._hook_type = hook_type  # type: ignore
        return func
    return decorator


def pre_execute(func: Callable[P, T]) -> Callable[P, T]:
    """Mark method as pre-execute hook."""
    return hook(HookType.PRE_EXECUTE)(func)


def post_execute(func: Callable[P, T]) -> Callable[P, T]:
    """Mark method as post-execute hook."""
    return hook(HookType.POST_EXECUTE)(func)


def on_error(func: Callable[P, T]) -> Callable[P, T]:
    """Mark method as error hook."""
    return hook(HookType.ON_ERROR)(func)


def on_memory_store(func: Callable[P, T]) -> Callable[P, T]:
    """Mark method as memory store hook."""
    return hook(HookType.ON_MEMORY_STORE)(func)


def with_hooks(
    hooks: AgentHooks,
    pre_hook: HookType = HookType.PRE_EXECUTE,
    post_hook: HookType = HookType.POST_EXECUTE,
    error_hook: HookType = HookType.ON_ERROR,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to wrap a function with hook execution.

    Usage:
        >>> @with_hooks(my_hooks)
        ... def execute_task(task: str) -> str:
        ...     return f"Completed: {task}"
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            hooks.execute(pre_hook, args=args, kwargs=kwargs)
            try:
                result = func(*args, **kwargs)
                hooks.execute(post_hook, args=args, kwargs=kwargs, result=result)
                return result
            except Exception as e:
                hooks.execute(error_hook, args=args, kwargs=kwargs, error=e)
                raise
        return wrapper
    return decorator
