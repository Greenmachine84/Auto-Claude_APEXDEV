"""Agent selector.

Selects best agent for a task.

Strategies:
- Round robin
- Least loaded
- Capability matching
- Affinity-based
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set

if TYPE_CHECKING:
    from orchestrator.pool.agent_pool import AgentInfo, AgentPool


logger = logging.getLogger(__name__)


class SelectionStrategy(ABC):
    """Base selection strategy."""
    
    @abstractmethod
    def select(
        self,
        agents: List["AgentInfo"],
        capabilities: Optional[Set[str]] = None,
    ) -> Optional["AgentInfo"]:
        """Select an agent."""
        pass


class RoundRobinStrategy(SelectionStrategy):
    """Round robin selection."""
    
    def __init__(self):
        """Initialize strategy."""
        self._index = 0
    
    def select(
        self,
        agents: List["AgentInfo"],
        capabilities: Optional[Set[str]] = None,
    ) -> Optional["AgentInfo"]:
        """Select next available agent."""
        available = [
            a for a in agents
            if a.is_available and
            (not capabilities or capabilities.issubset(a.capabilities))
        ]
        
        if not available:
            return None
        
        self._index = (self._index + 1) % len(available)
        return available[self._index]


class LeastLoadedStrategy(SelectionStrategy):
    """Least loaded selection."""
    
    def select(
        self,
        agents: List["AgentInfo"],
        capabilities: Optional[Set[str]] = None,
    ) -> Optional["AgentInfo"]:
        """Select least loaded agent."""
        available = [
            a for a in agents
            if a.is_available and
            (not capabilities or capabilities.issubset(a.capabilities))
        ]
        
        if not available:
            return None
        
        return min(available, key=lambda a: a.utilization)


class CapabilityMatchStrategy(SelectionStrategy):
    """Capability-based selection."""
    
    def select(
        self,
        agents: List["AgentInfo"],
        capabilities: Optional[Set[str]] = None,
    ) -> Optional["AgentInfo"]:
        """Select agent with best capability match."""
        if not capabilities:
            # Fall back to least loaded
            return LeastLoadedStrategy().select(agents, capabilities)
        
        available = [a for a in agents if a.is_available]
        if not available:
            return None
        
        # Score by capability overlap
        scored = []
        for agent in available:
            overlap = len(capabilities & agent.capabilities)
            if overlap >= len(capabilities):  # Has all required
                scored.append((overlap, agent))
        
        if not scored:
            return None
        
        # Return agent with most capabilities
        return max(scored, key=lambda x: x[0])[1]


@dataclass
class AgentSelector:
    """Agent selector.
    
    Selects best agent based on strategy.
    
    Example:
        selector = AgentSelector(pool)
        agent = selector.select(capabilities={"python"})
    """
    
    pool: "AgentPool"
    strategy: SelectionStrategy = None
    
    def __post_init__(self):
        """Initialize with default strategy."""
        if self.strategy is None:
            self.strategy = LeastLoadedStrategy()
    
    def select(
        self,
        capabilities: Optional[Set[str]] = None,
    ) -> Optional["AgentInfo"]:
        """Select an agent."""
        agents = self.pool.list_agents()
        return self.strategy.select(agents, capabilities)
    
    def set_strategy(self, strategy: SelectionStrategy) -> None:
        """Set selection strategy."""
        self.strategy = strategy
    
    def use_round_robin(self) -> None:
        """Use round robin strategy."""
        self.strategy = RoundRobinStrategy()
    
    def use_least_loaded(self) -> None:
        """Use least loaded strategy."""
        self.strategy = LeastLoadedStrategy()
    
    def use_capability_match(self) -> None:
        """Use capability match strategy."""
        self.strategy = CapabilityMatchStrategy()
