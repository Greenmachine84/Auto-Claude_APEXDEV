"""Pool scaler.

Dynamic scaling for agent pool.

Capabilities:
- Auto-scaling based on load
- Scale up/down policies
- Cooldown management
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from orchestrator.pool.agent_pool import AgentPool

from orchestrator.pool.config import PoolConfig


logger = logging.getLogger(__name__)


@dataclass
class ScalingDecision:
    """A scaling decision."""
    
    action: str  # "scale_up", "scale_down", "none"
    current_size: int
    target_size: int
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)


class PoolScaler:
    """Dynamic pool scaler.
    
    Automatically scales agent pool based on load.
    
    Example:
        scaler = PoolScaler(pool, config)
        await scaler.start()
    """
    
    def __init__(self, pool: "AgentPool", config: Optional[PoolConfig] = None):
        """Initialize scaler."""
        self.pool = pool
        self.config = config or pool.config
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_scale: Optional[datetime] = None
        self._decisions: list[ScalingDecision] = []
        
        logger.debug("PoolScaler initialized")
    
    @property
    def is_running(self) -> bool:
        """Check if scaler is running."""
        return self._running
    
    async def start(self) -> None:
        """Start the scaler."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scale_loop())
        
        logger.info("PoolScaler started")
    
    async def stop(self) -> None:
        """Stop the scaler."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        
        logger.info("PoolScaler stopped")
    
    async def evaluate(self) -> ScalingDecision:
        """Evaluate scaling decision."""
        current_size = self.pool.size
        utilization = self._get_utilization()
        
        # Check cooldown
        if self._in_cooldown():
            return ScalingDecision(
                action="none",
                current_size=current_size,
                target_size=current_size,
                reason="In cooldown period",
            )
        
        # Check scale up
        if utilization >= self.config.scale_up_threshold:
            if current_size < self.config.max_agents:
                return ScalingDecision(
                    action="scale_up",
                    current_size=current_size,
                    target_size=min(current_size + 1, self.config.max_agents),
                    reason=f"Utilization {utilization:.2f} >= threshold {self.config.scale_up_threshold}",
                )
        
        # Check scale down
        if utilization <= self.config.scale_down_threshold:
            if current_size > self.config.min_agents:
                return ScalingDecision(
                    action="scale_down",
                    current_size=current_size,
                    target_size=max(current_size - 1, self.config.min_agents),
                    reason=f"Utilization {utilization:.2f} <= threshold {self.config.scale_down_threshold}",
                )
        
        return ScalingDecision(
            action="none",
            current_size=current_size,
            target_size=current_size,
            reason="No scaling needed",
        )
    
    async def apply(self, decision: ScalingDecision) -> bool:
        """Apply scaling decision."""
        if decision.action == "none":
            return True
        
        try:
            if decision.action == "scale_up":
                for i in range(decision.target_size - decision.current_size):
                    agent_id = f"agent_{self.pool.size + i}"
                    await self.pool.add_agent(agent_id)
                    logger.info(f"Scaled up: added {agent_id}")
            
            elif decision.action == "scale_down":
                # Remove idle agents
                removed = 0
                for agent in self.pool.list_agents():
                    if removed >= decision.current_size - decision.target_size:
                        break
                    if agent.is_available:
                        await self.pool.remove_agent(agent.id)
                        logger.info(f"Scaled down: removed {agent.id}")
                        removed += 1
            
            self._last_scale = datetime.now()
            self._decisions.append(decision)
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply scaling: {e}")
            return False
    
    async def _scale_loop(self) -> None:
        """Scaling loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                decision = await self.evaluate()
                if decision.action != "none":
                    await self.apply(decision)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scale loop error: {e}")
    
    def _get_utilization(self) -> float:
        """Get current pool utilization."""
        if self.pool.size == 0:
            return 0.0
        return self.pool.busy_count / self.pool.size
    
    def _in_cooldown(self) -> bool:
        """Check if in cooldown period."""
        if not self._last_scale:
            return False
        elapsed = (datetime.now() - self._last_scale).total_seconds()
        return elapsed < self.config.scale_cooldown
    
    def get_history(self) -> list[Dict[str, Any]]:
        """Get scaling history."""
        return [
            {
                "action": d.action,
                "current_size": d.current_size,
                "target_size": d.target_size,
                "reason": d.reason,
                "timestamp": d.timestamp.isoformat(),
            }
            for d in self._decisions[-20:]
        ]
