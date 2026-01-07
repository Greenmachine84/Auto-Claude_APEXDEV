"""Result aggregator for orchestration.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections import Counter


@dataclass
class AggregatedResult:
    """Aggregated result from multiple agents."""
    source_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    results_by_agent: Dict[str, Any] = field(default_factory=dict)
    merged_output: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_count": self.source_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "results_by_agent": self.results_by_agent,
            "merged_output": self.merged_output,
            "conflicts": self.conflicts,
            "summary": self.summary,
        }
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.source_count == 0:
            return 0.0
        return self.success_count / self.source_count


class ResultAggregator:
    """Aggregates results from multiple agents.
    
    Provides various aggregation strategies for
    combining agent outputs.
    """
    
    def __init__(self):
        """Initialize aggregator."""
        pass
    
    def aggregate(
        self,
        results: List[Dict[str, Any]],
        strategy: str = "merge",
    ) -> AggregatedResult:
        """Aggregate multiple results.
        
        Args:
            results: List of {"agent_id": ..., "result": ...} dicts
            strategy: Aggregation strategy (merge, vote, first, latest)
            
        Returns:
            Aggregated result
        """
        aggregated = AggregatedResult(source_count=len(results))
        
        for item in results:
            agent_id = item.get("agent_id", "unknown")
            result = item.get("result", {})
            
            aggregated.results_by_agent[agent_id] = result
            
            if isinstance(result, dict) and result.get("status") == "error":
                aggregated.failure_count += 1
            elif isinstance(result, dict) and "error" in result:
                aggregated.failure_count += 1
            else:
                aggregated.success_count += 1
        
        # Apply aggregation strategy
        if strategy == "merge":
            aggregated.merged_output = self._merge_results(results)
        elif strategy == "vote":
            aggregated.merged_output = self._vote_results(results)
        elif strategy == "first":
            aggregated.merged_output = self._first_result(results)
        elif strategy == "latest":
            aggregated.merged_output = self._latest_result(results)
        else:
            aggregated.merged_output = self._merge_results(results)
        
        # Detect conflicts
        aggregated.conflicts = self._detect_conflicts(results)
        
        # Generate summary
        aggregated.summary = self._generate_summary(aggregated)
        
        return aggregated
    
    def _merge_results(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Merge results by combining all fields."""
        merged: Dict[str, Any] = {}
        
        for item in results:
            result = item.get("result", {})
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in merged:
                        merged[key] = value
                    elif isinstance(merged[key], list) and isinstance(value, list):
                        merged[key].extend(value)
                    elif isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key].update(value)
                    # else: keep first value
        
        return merged
    
    def _vote_results(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Vote on results (for categorical outputs)."""
        voted: Dict[str, Any] = {}
        field_values: Dict[str, List[Any]] = {}
        
        for item in results:
            result = item.get("result", {})
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in field_values:
                        field_values[key] = []
                    # Only vote on hashable values
                    try:
                        hash(value)
                        field_values[key].append(value)
                    except TypeError:
                        # Non-hashable, use first
                        if key not in voted:
                            voted[key] = value
        
        for key, values in field_values.items():
            if key not in voted and values:
                # Get most common value
                counter = Counter(values)
                voted[key] = counter.most_common(1)[0][0]
        
        return voted
    
    def _first_result(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Use first successful result."""
        for item in results:
            result = item.get("result", {})
            if isinstance(result, dict) and result.get("status") != "error":
                return result
        
        return results[0].get("result", {}) if results else {}
    
    def _latest_result(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Use latest result."""
        return results[-1].get("result", {}) if results else {}
    
    def _detect_conflicts(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Detect conflicting values across results."""
        conflicts: List[Dict[str, Any]] = []
        field_values: Dict[str, Dict[str, Any]] = {}  # field -> {agent_id: value}
        
        for item in results:
            agent_id = item.get("agent_id", "unknown")
            result = item.get("result", {})
            
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in field_values:
                        field_values[key] = {}
                    field_values[key][agent_id] = value
        
        # Find fields with different values
        for field, agent_values in field_values.items():
            unique_values = set()
            for v in agent_values.values():
                try:
                    hash(v)
                    unique_values.add(v)
                except TypeError:
                    unique_values.add(str(v))
            
            if len(unique_values) > 1:
                conflicts.append({
                    "field": field,
                    "values": agent_values,
                })
        
        return conflicts
    
    def _generate_summary(
        self,
        aggregated: AggregatedResult,
    ) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Aggregated {aggregated.source_count} agent results",
            f"Success: {aggregated.success_count}, Failed: {aggregated.failure_count}",
            f"Success rate: {aggregated.success_rate:.1%}",
        ]
        
        if aggregated.conflicts:
            lines.append(f"Conflicts detected: {len(aggregated.conflicts)}")
        
        return "\n".join(lines)
    
    def aggregate_by_type(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, List[Any]]:
        """Group results by their type/category.
        
        Args:
            results: List of agent results
            
        Returns:
            Results grouped by type
        """
        by_type: Dict[str, List[Any]] = {}
        
        for item in results:
            result = item.get("result", {})
            result_type = "unknown"
            
            if isinstance(result, dict):
                result_type = result.get("type", result.get("status", "unknown"))
            
            if result_type not in by_type:
                by_type[result_type] = []
            by_type[result_type].append(result)
        
        return by_type
