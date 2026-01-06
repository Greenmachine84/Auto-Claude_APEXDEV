"""Results Module.

Provides result collection and aggregation.
"""

from orchestrator.results.collector import ResultCollector
from orchestrator.results.aggregator import ResultAggregator
from orchestrator.results.validator import ResultValidator

__all__ = [
    "ResultCollector",
    "ResultAggregator",
    "ResultValidator",
]
