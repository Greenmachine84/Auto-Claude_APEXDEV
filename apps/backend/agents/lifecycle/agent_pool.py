"""Agent Pool Management.

Manages pools of reusable agent instances.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Provides:
- Agent pooling for performance
- Resource management
- Automatic cleanup
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from queue import Empty, Queue
from typing import Any

from ..base import BaseAgent
from ..registry import AgentFactory
from ..types import AgentType

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Configuration for agent pool."""

    min_size: int = 0
    max_size: int = 10
    idle_timeout_seconds: int = 300
    enable_prewarming: bool = False
    prewarm_count: int = 2

    def __post_init__(self) -> None:
        if self.min_size < 0:
            raise ValueError("min_size must be non-negative")
        if self.max_size < self.min_size:
            raise ValueError("max_size must be >= min_size")


@dataclass
class PooledAgent:
    """Wrapper for pooled agent with metadata."""

    agent: BaseAgent
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    use_count: int = 0

    def mark_used(self) -> None:
        """Mark agent as used."""
        self.last_used = datetime.now(timezone.utc)
        self.use_count += 1

    @property
    def idle_seconds(self) -> float:
        """Get seconds since last use."""
        return (datetime.now(timezone.utc) - self.last_used).total_seconds()


class AgentPool:
    """Pool of reusable agent instances.

    Manages a pool of pre-created agents for performance.
    Agents are acquired from the pool and released back when done.

    Usage:
        >>> pool = AgentPool(AgentType.CODER, max_size=5)
        >>> agent = pool.acquire()
        >>> try:
        ...     result = agent.run(context)
        ... finally:
        ...     pool.release(agent)
    """

    def __init__(
        self,
        agent_type: AgentType,
        config: PoolConfig | None = None,
        factory: AgentFactory | None = None,
    ):
        """Initialize agent pool.

        Args:
            agent_type: Type of agents in this pool
            config: Pool configuration
            factory: Agent factory to use
        """
        self.agent_type = agent_type
        self.config = config or PoolConfig()
        self._factory = factory or AgentFactory()
        self._pool: Queue[PooledAgent] = Queue(maxsize=self.config.max_size)
        self._active: dict[str, PooledAgent] = {}
        self._lock = threading.RLock()
        self._closed = False
        self._total_created = 0

        # Pre-warm pool if configured
        if self.config.enable_prewarming:
            self._prewarm()

    def _prewarm(self) -> None:
        """Pre-warm the pool with agents."""
        for _ in range(self.config.prewarm_count):
            if self._pool.qsize() < self.config.max_size:
                agent = self._create_agent()
                self._pool.put_nowait(PooledAgent(agent=agent))

    def _create_agent(self) -> BaseAgent:
        """Create a new agent instance."""
        with self._lock:
            self._total_created += 1
        return self._factory.create(self.agent_type)

    def acquire(self, timeout: float | None = None) -> BaseAgent:
        """Acquire an agent from the pool.

        Args:
            timeout: Maximum time to wait for an agent

        Returns:
            Agent instance

        Raises:
            RuntimeError: If pool is closed
            TimeoutError: If no agent available within timeout
        """
        if self._closed:
            raise RuntimeError("Pool is closed")

        try:
            pooled = self._pool.get(timeout=timeout)
        except Empty:
            # Pool empty, create new if under max
            with self._lock:
                if len(self._active) < self.config.max_size:
                    pooled = PooledAgent(agent=self._create_agent())
                else:
                    raise TimeoutError("No agents available in pool")

        pooled.mark_used()

        with self._lock:
            self._active[pooled.agent.id] = pooled

        logger.debug(f"Acquired agent: {pooled.agent.id}")
        return pooled.agent

    def release(self, agent: BaseAgent) -> None:
        """Release an agent back to the pool.

        Args:
            agent: Agent to release
        """
        with self._lock:
            if agent.id not in self._active:
                logger.warning(f"Unknown agent released: {agent.id}")
                return

            pooled = self._active.pop(agent.id)

        # Return to pool if healthy, otherwise discard
        if agent.is_healthy and not self._closed:
            try:
                self._pool.put_nowait(pooled)
                logger.debug(f"Released agent to pool: {agent.id}")
            except Exception:
                agent.cleanup()
        else:
            agent.cleanup()
            logger.debug(f"Discarded unhealthy agent: {agent.id}")

    def close(self) -> None:
        """Close the pool and cleanup all agents."""
        self._closed = True

        # Cleanup active agents
        with self._lock:
            for pooled in self._active.values():
                pooled.agent.cleanup()
            self._active.clear()

        # Cleanup pooled agents
        while not self._pool.empty():
            try:
                pooled = self._pool.get_nowait()
                pooled.agent.cleanup()
            except Empty:
                break

        logger.info(f"Pool closed: {self.agent_type.value}")

    @property
    def available_count(self) -> int:
        """Get number of available agents."""
        return self._pool.qsize()

    @property
    def active_count(self) -> int:
        """Get number of active agents."""
        with self._lock:
            return len(self._active)

    @property
    def total_count(self) -> int:
        """Get total agents (available + active)."""
        return self.available_count + self.active_count

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics."""
        return {
            "agent_type": self.agent_type.value,
            "available": self.available_count,
            "active": self.active_count,
            "total": self.total_count,
            "max_size": self.config.max_size,
            "total_created": self._total_created,
            "closed": self._closed,
        }

    def __enter__(self) -> "AgentPool":
        return self

    def __exit__(self, *args) -> None:
        self.close()
