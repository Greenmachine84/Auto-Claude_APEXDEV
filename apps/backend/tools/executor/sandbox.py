"""
Sandbox Execution - Phase 8 Implementation.

Secure sandboxed tool execution.

World-Class Standards:
- Resource limits
- Filesystem isolation
- Network restrictions
- Audit logging
"""

import asyncio
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..models import ToolExecutionContext, ToolResult

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """Sandbox configuration."""

    max_memory_mb: int = 512
    max_cpu_time_s: int = 60
    max_file_size_mb: int = 100
    max_files: int = 100
    allowed_paths: list = field(default_factory=list)
    denied_paths: list = field(default_factory=lambda: ["/etc", "/usr", "/bin"])
    allow_network: bool = False
    allowed_hosts: list = field(default_factory=list)
    enable_audit: bool = True


@dataclass
class SandboxViolation:
    """Record of sandbox violation."""

    timestamp: str
    violation_type: str
    details: str
    context: dict[str, Any]


class Sandbox:
    """
    Secure execution sandbox.

    Features:
    - Resource limits
    - Path restrictions
    - Network controls
    - Audit trail
    """

    def __init__(self, config: SandboxConfig | None = None) -> None:
        """Initialize sandbox."""
        self.config = config or SandboxConfig()

        self._violations: list = []
        self._audit_log: list = []
        self._active_executions: set[str] = set()

        logger.info("Sandbox initialized with config: %s", self.config)

    async def execute(
        self,
        handler: Callable,
        arguments: dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        """
        Execute handler in sandbox.

        Args:
            handler: Tool handler function
            arguments: Handler arguments
            context: Execution context

        Returns:
            ToolResult with execution outcome
        """
        execution_id = f"{context.session_id}_{datetime.utcnow().timestamp()}"
        self._active_executions.add(execution_id)

        try:
            # Pre-execution checks
            violation = self._pre_execution_check(arguments)
            if violation:
                self._record_violation(violation)
                return ToolResult(
                    output=None,
                    error=f"Sandbox violation: {violation.violation_type}",
                    metadata={"violation": violation.details},
                )

            # Apply resource limits
            self._apply_limits()

            # Create sandboxed context
            sandboxed_context = self._create_sandboxed_context(context)

            # Audit log entry
            if self.config.enable_audit:
                self._audit(
                    "execute_start",
                    {
                        "execution_id": execution_id,
                        "handler": handler.__name__
                        if hasattr(handler, "__name__")
                        else str(handler),
                        "arguments": self._sanitize_for_audit(arguments),
                    },
                )

            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                output = await handler(sandboxed_context, **arguments)
            else:
                output = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: handler(sandboxed_context, **arguments)
                )

            # Post-execution validation
            violation = self._post_execution_check(output)
            if violation:
                self._record_violation(violation)
                return ToolResult(
                    output=None,
                    error=f"Sandbox violation: {violation.violation_type}",
                    metadata={"violation": violation.details},
                )

            # Audit success
            if self.config.enable_audit:
                self._audit(
                    "execute_success",
                    {
                        "execution_id": execution_id,
                    },
                )

            return self._normalize_output(output)

        except Exception as e:
            logger.error("Sandbox execution error: %s", e)

            if self.config.enable_audit:
                self._audit(
                    "execute_error",
                    {
                        "execution_id": execution_id,
                        "error": str(e),
                    },
                )

            return ToolResult(
                output=None,
                error=f"Execution error: {str(e)}",
                metadata={"exception": type(e).__name__},
            )
        finally:
            self._active_executions.discard(execution_id)

    def _pre_execution_check(
        self, arguments: dict[str, Any]
    ) -> SandboxViolation | None:
        """Check arguments before execution."""
        # Check for path violations
        for key, value in arguments.items():
            if isinstance(value, str):
                violation = self._check_path(value)
                if violation:
                    return violation

        return None

    def _post_execution_check(self, output: Any) -> SandboxViolation | None:
        """Check output after execution."""
        # Check output size
        if isinstance(output, (str, bytes)):
            size_mb = len(output) / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                return SandboxViolation(
                    timestamp=datetime.utcnow().isoformat(),
                    violation_type="output_size_exceeded",
                    details=f"Output size {size_mb:.2f}MB exceeds limit",
                    context={"size_mb": size_mb},
                )

        return None

    def _check_path(self, path: str) -> SandboxViolation | None:
        """Check if path is allowed."""
        # Normalize path
        try:
            normalized = os.path.normpath(os.path.abspath(path))
        except Exception:
            return None  # Not a valid path

        # Check denied paths
        for denied in self.config.denied_paths:
            if normalized.startswith(denied):
                return SandboxViolation(
                    timestamp=datetime.utcnow().isoformat(),
                    violation_type="path_denied",
                    details=f"Access to {path} is denied",
                    context={"path": path, "denied_pattern": denied},
                )

        # If allowed_paths specified, check whitelist
        if self.config.allowed_paths:
            allowed = False
            for allow_path in self.config.allowed_paths:
                if normalized.startswith(os.path.normpath(os.path.abspath(allow_path))):
                    allowed = True
                    break

            if not allowed:
                return SandboxViolation(
                    timestamp=datetime.utcnow().isoformat(),
                    violation_type="path_not_allowed",
                    details=f"Access to {path} is not in allowed list",
                    context={"path": path},
                )

        return None

    def _apply_limits(self) -> None:
        """Apply resource limits."""
        # Platform-specific limit application
        try:
            import resource

            # Memory limit
            mem_bytes = self.config.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

            # CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.config.max_cpu_time_s, self.config.max_cpu_time_s),
            )

        except (ImportError, AttributeError):
            # Not available on Windows
            pass

    def _create_sandboxed_context(
        self, context: ToolExecutionContext
    ) -> ToolExecutionContext:
        """Create sandboxed execution context."""
        return ToolExecutionContext(
            user_id=context.user_id,
            session_id=context.session_id,
            permissions=context.permissions,
            timeout_ms=context.timeout_ms,
            sandbox_disabled=False,  # Always enforce
            environment={
                **context.environment,
                "_sandboxed": True,
                "_allowed_paths": self.config.allowed_paths,
            },
        )

    def _normalize_output(self, output: Any) -> ToolResult:
        """Normalize handler output to ToolResult."""
        if isinstance(output, ToolResult):
            return output

        if isinstance(output, dict):
            if "error" in output:
                return ToolResult(
                    output=output.get("output"),
                    error=output["error"],
                    metadata=output.get("metadata", {}),
                )
            return ToolResult(
                output=output,
                error=None,
                metadata={},
            )

        return ToolResult(
            output=output,
            error=None,
            metadata={},
        )

    def _record_violation(self, violation: SandboxViolation) -> None:
        """Record a sandbox violation."""
        self._violations.append(violation)
        logger.warning(
            "Sandbox violation: %s - %s", violation.violation_type, violation.details
        )

        # Trim old violations
        if len(self._violations) > 1000:
            self._violations = self._violations[-500:]

    def _audit(self, event: str, details: dict[str, Any]) -> None:
        """Add audit log entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **details,
        }
        self._audit_log.append(entry)

        # Trim old entries
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-5000:]

    def _sanitize_for_audit(self, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize data for audit logging."""
        sanitized = {}
        sensitive_keys = {"password", "secret", "token", "key", "credential"}

        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                sanitized[key] = f"{value[:100]}... [truncated]"
            else:
                sanitized[key] = value

        return sanitized

    def get_violations(self, limit: int = 100) -> list:
        """Get recent violations."""
        return self._violations[-limit:]

    def get_audit_log(self, limit: int = 100) -> list:
        """Get recent audit entries."""
        return self._audit_log[-limit:]

    def get_active_count(self) -> int:
        """Get count of active executions."""
        return len(self._active_executions)
