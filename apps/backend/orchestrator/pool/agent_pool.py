"""Agent pool implementation.

Manages a pool of worker agents.

Capabilities:
- Agent lifecycle management
- Dynamic scaling
- Health monitoring
- Load balancing
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from orchestrator.pool.config import PoolConfig


logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent status values."""
    
    IDLE = "idle"
    BUSY = "busy"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Information about an agent."""
    
    id: str
    name: str
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Capabilities
    capabilities: Set[str] = field(default_factory=set)
    max_concurrent: int = 1
    current_tasks: int = 0
    
    # Metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_time_ms: float = 0.0
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available."""
        return (
            self.status == AgentStatus.IDLE and
            self.current_tasks < self.max_concurrent
        )
    
    @property
    def utilization(self) -> float:
        """Get agent utilization."""
        if self.max_concurrent == 0:
            return 0.0
        return self.current_tasks / self.max_concurrent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "capabilities": list(self.capabilities),
            "max_concurrent": self.max_concurrent,
            "current_tasks": self.current_tasks,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "utilization": self.utilization,
        }


class AgentPool:
    """Pool of worker agents.
    
    Manages agent lifecycle and task distribution.
    
    Example:
        pool = AgentPool(config)
        await pool.start()
        
        agent = await pool.acquire()
        # use agent
        await pool.release(agent.id)
    """
    
    def __init__(self, config: Optional[PoolConfig] = None):
        """Initialize pool."""
        self.config = config or PoolConfig()
        self._agents: Dict[str, AgentInfo] = {}
        self._lock = asyncio.Lock()
        self._available = asyncio.Condition(self._lock)
        self._running = False
        self._health_task: Optional[asyncio.Task] = None
        
        logger.info(f"AgentPool initialized with config: {self.config}")
    
    @property
    def size(self) -> int:
        """Get pool size."""
        return len(self._agents)
    
    @property
    def available_count(self) -> int:
        """Get available agent count."""
        return sum(1 for a in self._agents.values() if a.is_available)
    
    @property
    def busy_count(self) -> int:
        """Get busy agent count."""
        return sum(1 for a in self._agents.values() if a.status == AgentStatus.BUSY)
    
    async def start(self) -> None:
        """Start the pool."""
        if self._running:
            return
        
        self._running = True
        
        # Create initial agents
        for i in range(self.config.min_agents):
            await self._create_agent(f"agent_{i}")
        
        # Start health check
        if self.config.health_check_interval > 0:
            self._health_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"AgentPool started with {self.size} agents")
    
    async def stop(self) -> None:
        """Stop the pool."""
        if not self._running:
            return
        
        self._running = False
        
        # Stop health check
        if self._health_task:
            self._health_task.cancel()
            self._health_task = None
        
        # Stop all agents
        async with self._lock:
            for agent in self._agents.values():
                agent.status = AgentStatus.STOPPING
            self._agents.clear()
        
        logger.info("AgentPool stopped")
    
    async def acquire(
        self,
        capabilities: Optional[Set[str]] = None,
        timeout: Optional[float] = None,
    ) -> Optional[AgentInfo]:
        """Acquire an available agent."""
        timeout = timeout or self.config.acquire_timeout
        
        async with self._available:
            deadline = asyncio.get_event_loop().time() + timeout
            
            while asyncio.get_event_loop().time() < deadline:
                # Find available agent
                agent = self._find_available(capabilities)
                if agent:
                    agent.status = AgentStatus.BUSY
                    agent.current_tasks += 1
                    agent.last_active = datetime.now()
                    return agent
                
                # Wait for availability
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    break
                
                try:
                    await asyncio.wait_for(
                        self._available.wait(),
                        timeout=remaining,
                    )
                except asyncio.TimeoutError:
                    break
        
        return None
    
    async def release(self, agent_id: str) -> None:
        """Release an agent back to pool."""
        async with self._available:
            agent = self._agents.get(agent_id)
            if agent:
                agent.current_tasks = max(0, agent.current_tasks - 1)
                if agent.current_tasks == 0:
                    agent.status = AgentStatus.IDLE
                agent.last_active = datetime.now()
                self._available.notify()
    
    async def add_agent(self, agent_id: str, **kwargs: Any) -> AgentInfo:
        """Add agent to pool."""
        return await self._create_agent(agent_id, **kwargs)
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from pool."""
        async with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                return True
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """List all agents."""
        return list(self._agents.values())
    
    async def _create_agent(self, agent_id: str, **kwargs: Any) -> AgentInfo:
        """Create a new agent."""
        async with self._lock:
            agent = AgentInfo(
                id=agent_id,
                name=kwargs.get("name", agent_id),
                capabilities=kwargs.get("capabilities", set()),
                max_concurrent=kwargs.get("max_concurrent", 1),
            )
            self._agents[agent_id] = agent
            self._available.notify()
            return agent
    
    def _find_available(self, capabilities: Optional[Set[str]] = None) -> Optional[AgentInfo]:
        """Find available agent with capabilities."""
        for agent in self._agents.values():
            if not agent.is_available:
                continue
            if capabilities and not capabilities.issubset(agent.capabilities):
                continue
            return agent
        return None
    
    async def _health_check_loop(self) -> None:
        """Health check loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._check_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _check_health(self) -> None:
        """Check health of all agents."""
        async with self._lock:
            for agent in self._agents.values():
                # Check for stale agents
                idle_time = (datetime.now() - agent.last_active).total_seconds()
                if idle_time > self.config.max_idle_time:
                    if agent.status == AgentStatus.IDLE:
                        agent.status = AgentStatus.OFFLINE
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pool metrics."""
        return {
            "size": self.size,
            "available": self.available_count,
            "busy": self.busy_count,
            "utilization": self.busy_count / max(1, self.size),
            "agents": [a.to_dict() for a in self._agents.values()],
        }
