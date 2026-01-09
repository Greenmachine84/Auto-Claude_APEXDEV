"""Orchestration Module for enterprise agents.

Provides agent coordination and pipeline management capabilities.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from .agent_coordinator import AgentCoordinator, CoordinationResult
from .orchestrator_agent import OrchestratorAgent
from .pipeline_manager import Pipeline, PipelineManager, PipelineStage
from .result_aggregator import AggregatedResult, ResultAggregator

__all__ = [
    # Agent
    "OrchestratorAgent",
    # Coordinator
    "AgentCoordinator",
    "CoordinationResult",
    # Aggregator
    "ResultAggregator",
    "AggregatedResult",
    # Pipeline
    "PipelineManager",
    "Pipeline",
    "PipelineStage",
]
