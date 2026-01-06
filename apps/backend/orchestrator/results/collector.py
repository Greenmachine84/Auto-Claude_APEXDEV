"""Result collector.

Collects task results.

Capabilities:
- Result storage
- Streaming results
- Result callbacks
- Persistence
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class CollectedResult:
    """A collected result."""
    
    task_id: str
    result: Any
    success: bool
    collected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResultCollector:
    """Collect task results.
    
    Gathers and stores results from task execution.
    
    Example:
        collector = ResultCollector()
        collector.collect(task_id, result)
        results = collector.get_all()
    """
    
    def __init__(self, max_results: int = 10000):
        """Initialize collector."""
        self.max_results = max_results
        self._results: Dict[str, CollectedResult] = {}
        self._callbacks: List[Callable[[CollectedResult], None]] = []
        self._lock = asyncio.Lock()
        
        logger.debug(f"ResultCollector initialized with max_results={max_results}")
    
    async def collect(
        self,
        task_id: str,
        result: Any,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CollectedResult:
        """Collect a result."""
        collected = CollectedResult(
            task_id=task_id,
            result=result,
            success=success,
            metadata=metadata or {},
        )
        
        async with self._lock:
            # Enforce limit
            if len(self._results) >= self.max_results:
                # Remove oldest
                oldest = min(
                    self._results.values(),
                    key=lambda r: r.collected_at,
                )
                del self._results[oldest.task_id]
            
            self._results[task_id] = collected
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(collected)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        return collected
    
    def get(self, task_id: str) -> Optional[CollectedResult]:
        """Get result by task ID."""
        return self._results.get(task_id)
    
    def get_all(self) -> List[CollectedResult]:
        """Get all results."""
        return list(self._results.values())
    
    def get_successful(self) -> List[CollectedResult]:
        """Get successful results."""
        return [r for r in self._results.values() if r.success]
    
    def get_failed(self) -> List[CollectedResult]:
        """Get failed results."""
        return [r for r in self._results.values() if not r.success]
    
    async def wait_for(
        self,
        task_id: str,
        timeout: float = 60.0,
    ) -> Optional[CollectedResult]:
        """Wait for a result."""
        deadline = asyncio.get_event_loop().time() + timeout
        
        while asyncio.get_event_loop().time() < deadline:
            result = self.get(task_id)
            if result:
                return result
            await asyncio.sleep(0.1)
        
        return None
    
    def add_callback(
        self,
        callback: Callable[[CollectedResult], None],
    ) -> None:
        """Add result callback."""
        self._callbacks.append(callback)
    
    def remove_callback(
        self,
        callback: Callable[[CollectedResult], None],
    ) -> None:
        """Remove result callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def clear(self) -> int:
        """Clear all results."""
        async with self._lock:
            count = len(self._results)
            self._results.clear()
            return count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collector metrics."""
        results = list(self._results.values())
        return {
            "total": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "max_results": self.max_results,
            "callback_count": len(self._callbacks),
        }
