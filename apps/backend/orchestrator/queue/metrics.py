"""Queue metrics.

Tracks queue performance metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class QueueMetrics:
    """Metrics for task queue.
    
    Tracks:
    - Enqueue/dequeue counts
    - Wait times
    - Queue size over time
    """
    
    # Counters
    tasks_enqueued: int = 0
    tasks_dequeued: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_cancelled: int = 0
    tasks_timeout: int = 0
    
    # Current state
    current_size: int = 0
    max_size_seen: int = 0
    
    # Timing
    total_wait_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0
    
    # History
    size_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def record_wait_time(self, wait_ms: float) -> None:
        """Record task wait time."""
        self.total_wait_time_ms += wait_ms
    
    def record_processing_time(self, time_ms: float) -> None:
        """Record task processing time."""
        self.total_processing_time_ms += time_ms
    
    def record_size(self) -> None:
        """Record current queue size."""
        self.max_size_seen = max(self.max_size_seen, self.current_size)
        self.size_history.append({
            "timestamp": datetime.now().isoformat(),
            "size": self.current_size,
        })
        
        # Keep last 100 entries
        if len(self.size_history) > 100:
            self.size_history = self.size_history[-100:]
    
    @property
    def throughput(self) -> float:
        """Get tasks per second throughput."""
        if self.tasks_completed == 0:
            return 0.0
        return self.tasks_completed / (self.total_processing_time_ms / 1000)
    
    @property
    def avg_wait_time_ms(self) -> float:
        """Get average wait time."""
        total = self.tasks_dequeued
        if total == 0:
            return 0.0
        return self.total_wait_time_ms / total
    
    @property
    def avg_processing_time_ms(self) -> float:
        """Get average processing time."""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return self.total_processing_time_ms / total
    
    @property
    def success_rate(self) -> float:
        """Get success rate."""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return self.tasks_completed / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tasks_enqueued": self.tasks_enqueued,
            "tasks_dequeued": self.tasks_dequeued,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "tasks_cancelled": self.tasks_cancelled,
            "tasks_timeout": self.tasks_timeout,
            "current_size": self.current_size,
            "max_size_seen": self.max_size_seen,
            "avg_wait_time_ms": self.avg_wait_time_ms,
            "avg_processing_time_ms": self.avg_processing_time_ms,
            "throughput": self.throughput,
            "success_rate": self.success_rate,
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.tasks_enqueued = 0
        self.tasks_dequeued = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.tasks_cancelled = 0
        self.tasks_timeout = 0
        self.current_size = 0
        self.max_size_seen = 0
        self.total_wait_time_ms = 0.0
        self.total_processing_time_ms = 0.0
        self.size_history.clear()
