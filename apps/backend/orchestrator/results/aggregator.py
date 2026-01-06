"""Result aggregator.

Aggregates multiple results.

Capabilities:
- Combine results
- Statistics
- Grouping
- Transformations
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from orchestrator.results.collector import CollectedResult


logger = logging.getLogger(__name__)


@dataclass
class AggregatedResult:
    """An aggregated result."""
    
    name: str
    results: List[CollectedResult]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def count(self) -> int:
        """Get result count."""
        return len(self.results)
    
    @property
    def success_count(self) -> int:
        """Get successful result count."""
        return sum(1 for r in self.results if r.success)
    
    @property
    def failure_count(self) -> int:
        """Get failed result count."""
        return sum(1 for r in self.results if not r.success)
    
    @property
    def success_rate(self) -> float:
        """Get success rate."""
        if self.count == 0:
            return 0.0
        return self.success_count / self.count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "count": self.count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "metadata": self.metadata,
        }


class ResultAggregator:
    """Aggregate results.
    
    Combines and analyzes results.
    
    Example:
        aggregator = ResultAggregator()
        aggregated = aggregator.aggregate(results)
    """
    
    def __init__(self):
        """Initialize aggregator."""
        self._transformers: Dict[str, Callable] = {}
        
        logger.debug("ResultAggregator initialized")
    
    def aggregate(
        self,
        results: List[CollectedResult],
        name: str = "default",
    ) -> AggregatedResult:
        """Aggregate results."""
        return AggregatedResult(
            name=name,
            results=results,
        )
    
    def group_by(
        self,
        results: List[CollectedResult],
        key: Callable[[CollectedResult], str],
    ) -> Dict[str, AggregatedResult]:
        """Group results by key."""
        groups: Dict[str, List[CollectedResult]] = {}
        
        for result in results:
            group_key = key(result)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(result)
        
        return {
            k: AggregatedResult(name=k, results=v)
            for k, v in groups.items()
        }
    
    def filter(
        self,
        results: List[CollectedResult],
        predicate: Callable[[CollectedResult], bool],
    ) -> List[CollectedResult]:
        """Filter results."""
        return [r for r in results if predicate(r)]
    
    def map(
        self,
        results: List[CollectedResult],
        transform: Callable[[CollectedResult], Any],
    ) -> List[Any]:
        """Map results to values."""
        return [transform(r) for r in results]
    
    def reduce(
        self,
        results: List[CollectedResult],
        reducer: Callable[[Any, CollectedResult], Any],
        initial: Any = None,
    ) -> Any:
        """Reduce results to single value."""
        value = initial
        for result in results:
            value = reducer(value, result)
        return value
    
    def statistics(
        self,
        results: List[CollectedResult],
    ) -> Dict[str, Any]:
        """Calculate result statistics."""
        if not results:
            return {
                "count": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
            }
        
        success_count = sum(1 for r in results if r.success)
        
        return {
            "count": len(results),
            "success_count": success_count,
            "failure_count": len(results) - success_count,
            "success_rate": success_count / len(results),
        }
    
    def register_transformer(
        self,
        name: str,
        transformer: Callable[[List[CollectedResult]], Any],
    ) -> None:
        """Register a result transformer."""
        self._transformers[name] = transformer
    
    def transform(
        self,
        results: List[CollectedResult],
        transformer_name: str,
    ) -> Any:
        """Apply registered transformer."""
        transformer = self._transformers.get(transformer_name)
        if not transformer:
            raise ValueError(f"Unknown transformer: {transformer_name}")
        return transformer(results)
