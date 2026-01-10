"""Agent Supervisor.

Provides supervised execution for agents.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Provides:
- Timeout management
- Error recovery
- Health monitoring
- Restart policies
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from ..base import BaseAgent, ExecutionContext
from ..types import AgentResult, AgentStatus
from .lifecycle_manager import LifecycleEvent, LifecycleManager

logger = logging.getLogger(__name__)


class RestartPolicy(Enum):
    """Agent restart policies."""

    NEVER = auto()  # Never restart
    ON_FAILURE = auto()  # Restart only on failure
    ALWAYS = auto()  # Always restart (for long-running)
    EXPONENTIAL_BACKOFF = auto()  # Restart with increasing delay


@dataclass
class SupervisorConfig:
    """Configuration for agent supervisor."""

    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    max_restarts: int = 3
    restart_delay_seconds: float = 1.0
    max_restart_delay_seconds: float = 60.0
    timeout_seconds: float | None = None
    health_check_interval_seconds: float = 30.0
    enable_health_checks: bool = True


@dataclass
class SupervisionRecord:
    """Record of supervision activity."""

    agent_id: str
    event: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    restart_count: int = 0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentSupervisor:
    """Supervises agent execution with recovery.

    Monitors agent health and handles failures according to
    restart policy. Integrates with lifecycle manager.

    Usage:
        >>> supervisor = AgentSupervisor(agent, config=SupervisorConfig(
        ...     restart_policy=RestartPolicy.ON_FAILURE,
        ...     max_restarts=3,
        ... ))
        >>> result = supervisor.run(context)
    """

    def __init__(
        self,
        agent: BaseAgent,
        config: SupervisorConfig | None = None,
        lifecycle_manager: LifecycleManager | None = None,
    ):
        """Initialize supervisor.

        Args:
            agent: Agent to supervise
            config: Supervisor configuration
            lifecycle_manager: Optional lifecycle manager
        """
        self.agent = agent
        self.config = config or SupervisorConfig()
        self._lifecycle = lifecycle_manager or LifecycleManager()
        self._restart_count = 0
        self._current_delay = self.config.restart_delay_seconds
        self._records: list[SupervisionRecord] = []
        self._running = False
        self._stop_requested = False
        self._health_thread: threading.Thread | None = None

        self._lifecycle.track(agent)

    def run(self, context: ExecutionContext) -> AgentResult:
        """Run agent with supervision.

        Args:
            context: Execution context

        Returns:
            AgentResult from execution
        """
        self._running = True
        self._stop_requested = False
        self._restart_count = 0

        # Start health monitoring if enabled
        if self.config.enable_health_checks:
            self._start_health_monitoring()

        try:
            return self._execute_with_supervision(context)
        finally:
            self._running = False
            self._stop_health_monitoring()

    def _execute_with_supervision(
        self,
        context: ExecutionContext,
    ) -> AgentResult:
        """Execute with restart handling."""
        while not self._stop_requested:
            try:
                self._lifecycle.emit(LifecycleEvent.STARTED, self.agent)
                self._record("started")

                result = self._execute_with_timeout(context)

                self._lifecycle.emit(LifecycleEvent.COMPLETED, self.agent)
                self._record("completed")

                return result

            except Exception as e:
                error_msg = str(e)
                self._lifecycle.emit(
                    LifecycleEvent.FAILED,
                    self.agent,
                    metadata={"error": error_msg},
                )
                self._record("failed", error=error_msg)

                if self._should_restart(e):
                    self._do_restart()
                else:
                    from ..types import ErrorCode, ErrorResult

                    return ErrorResult(
                        message=error_msg,
                        code=ErrorCode.EXECUTION_ERROR,
                        recoverable=False,
                    )

        # Stop requested
        from ..types import ErrorCode, ErrorResult

        return ErrorResult(
            message="Execution stopped by supervisor",
            code=ErrorCode.TIMEOUT,
            recoverable=True,
        )

    def _execute_with_timeout(
        self,
        context: ExecutionContext,
    ) -> AgentResult:
        """Execute with optional timeout."""
        if self.config.timeout_seconds is None:
            return self.agent.run(context)

        result: AgentResult | None = None
        exception: Exception | None = None

        def run_agent() -> None:
            nonlocal result, exception
            try:
                result = self.agent.run(context)
            except Exception as e:
                exception = e

        thread = threading.Thread(target=run_agent)
        thread.start()
        thread.join(timeout=self.config.timeout_seconds)

        if thread.is_alive():
            self.agent.terminate()
            raise TimeoutError(
                f"Agent execution timed out after {self.config.timeout_seconds}s"
            )

        if exception:
            raise exception

        assert result is not None
        return result

    def _should_restart(self, error: Exception) -> bool:
        """Determine if agent should be restarted."""
        if self._stop_requested:
            return False

        if self._restart_count >= self.config.max_restarts:
            logger.warning(
                f"Max restarts ({self.config.max_restarts}) reached for {self.agent.id}"
            )
            return False

        policy = self.config.restart_policy

        if policy == RestartPolicy.NEVER:
            return False
        elif policy == RestartPolicy.ON_FAILURE:
            return True
        elif policy == RestartPolicy.ALWAYS:
            return True
        elif policy == RestartPolicy.EXPONENTIAL_BACKOFF:
            return True

        return False

    def _do_restart(self) -> None:
        """Perform agent restart."""
        self._restart_count += 1

        # Calculate delay
        if self.config.restart_policy == RestartPolicy.EXPONENTIAL_BACKOFF:
            delay = min(
                self._current_delay * (2 ** (self._restart_count - 1)),
                self.config.max_restart_delay_seconds,
            )
        else:
            delay = self.config.restart_delay_seconds

        logger.info(
            f"Restarting agent {self.agent.id} in {delay}s "
            f"(attempt {self._restart_count}/{self.config.max_restarts})"
        )

        self._lifecycle.emit(
            LifecycleEvent.RESTARTED,
            self.agent,
            metadata={"restart_count": self._restart_count, "delay": delay},
        )
        self._record("restarting", metadata={"delay": delay})

        time.sleep(delay)

        # Re-initialize agent
        self.agent.cleanup()
        self.agent.initialize()

    def _start_health_monitoring(self) -> None:
        """Start health monitoring thread."""

        def monitor() -> None:
            while self._running and not self._stop_requested:
                if not self.agent.is_healthy:
                    logger.warning(f"Agent unhealthy: {self.agent.id}")
                    self._record("unhealthy")
                time.sleep(self.config.health_check_interval_seconds)

        self._health_thread = threading.Thread(target=monitor, daemon=True)
        self._health_thread.start()

    def _stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        self._stop_requested = True
        if self._health_thread and self._health_thread.is_alive():
            self._health_thread.join(timeout=1.0)

    def stop(self) -> None:
        """Request supervisor to stop."""
        self._stop_requested = True
        if self.agent.status == AgentStatus.RUNNING:
            self.agent.pause()

    def _record(
        self,
        event: str,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record supervision event."""
        record = SupervisionRecord(
            agent_id=self.agent.id,
            event=event,
            restart_count=self._restart_count,
            error=error,
            metadata=metadata or {},
        )
        self._records.append(record)

        # Keep bounded
        if len(self._records) > 100:
            self._records = self._records[-100:]

    def get_stats(self) -> dict[str, Any]:
        """Get supervision statistics."""
        return {
            "agent_id": self.agent.id,
            "running": self._running,
            "restart_count": self._restart_count,
            "max_restarts": self.config.max_restarts,
            "policy": self.config.restart_policy.name,
            "records_count": len(self._records),
        }

    def get_records(self, limit: int | None = None) -> list[SupervisionRecord]:
        """Get supervision records."""
        if limit:
            return self._records[-limit:]
        return list(self._records)
