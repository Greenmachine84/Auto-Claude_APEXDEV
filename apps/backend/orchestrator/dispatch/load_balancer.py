"""Load balancer.

Balances load across agents.

Strategies:
- Round robin
- Least connections
- Weighted
- Random
"""

import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestrator.pool.agent_pool import AgentInfo


logger = logging.getLogger(__name__)


class BalancingStrategy(ABC):
    """Base load balancing strategy."""
    
    @abstractmethod
    def select(self, agents: List["AgentInfo"]) -> Optional["AgentInfo"]:
        """Select an agent."""
        pass


class RoundRobinBalancer(BalancingStrategy):
    """Round robin load balancing."""
    
    def __init__(self):
        """Initialize balancer."""
        self._index = 0
    
    def select(self, agents: List["AgentInfo"]) -> Optional["AgentInfo"]:
        """Select next agent."""
        available = [a for a in agents if a.is_available]
        if not available:
            return None
        
        self._index = (self._index + 1) % len(available)
        return available[self._index]


class LeastConnectionsBalancer(BalancingStrategy):
    """Least connections load balancing."""
    
    def select(self, agents: List["AgentInfo"]) -> Optional["AgentInfo"]:
        """Select least loaded agent."""
        available = [a for a in agents if a.is_available]
        if not available:
            return None
        
        return min(available, key=lambda a: a.current_tasks)


class WeightedBalancer(BalancingStrategy):
    """Weighted load balancing."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize with weights."""
        self._weights = weights or {}
    
    def set_weight(self, agent_id: str, weight: float) -> None:
        """Set agent weight."""
        self._weights[agent_id] = weight
    
    def select(self, agents: List["AgentInfo"]) -> Optional["AgentInfo"]:
        """Select agent by weight."""
        available = [a for a in agents if a.is_available]
        if not available:
            return None
        
        # Get weights (default 1.0)
        weighted = [
            (a, self._weights.get(a.id, 1.0))
            for a in available
        ]
        
        # Select by weight
        total = sum(w for _, w in weighted)
        r = random.uniform(0, total)
        
        cumulative = 0
        for agent, weight in weighted:
            cumulative += weight
            if r <= cumulative:
                return agent
        
        return weighted[-1][0]


class RandomBalancer(BalancingStrategy):
    """Random load balancing."""
    
    def select(self, agents: List["AgentInfo"]) -> Optional["AgentInfo"]:
        """Select random agent."""
        available = [a for a in agents if a.is_available]
        if not available:
            return None
        
        return random.choice(available)


@dataclass
class LoadBalancer:
    """Load balancer.
    
    Distributes load across agents.
    
    Example:
        balancer = LoadBalancer()
        agent = balancer.select(agents)
    """
    
    strategy: BalancingStrategy = field(default_factory=LeastConnectionsBalancer)
    
    def select(self, agents: List["AgentInfo"]) -> Optional["AgentInfo"]:
        """Select an agent."""
        return self.strategy.select(agents)
    
    def use_round_robin(self) -> None:
        """Use round robin strategy."""
        self.strategy = RoundRobinBalancer()
    
    def use_least_connections(self) -> None:
        """Use least connections strategy."""
        self.strategy = LeastConnectionsBalancer()
    
    def use_weighted(self, weights: Optional[Dict[str, float]] = None) -> None:
        """Use weighted strategy."""
        self.strategy = WeightedBalancer(weights)
    
    def use_random(self) -> None:
        """Use random strategy."""
        self.strategy = RandomBalancer()
