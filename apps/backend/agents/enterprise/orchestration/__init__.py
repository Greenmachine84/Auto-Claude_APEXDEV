"""Orchestration Module for enterprise agents.

Provides agent coordination and pipeline management capabilities.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from .orchestrator_agent import OrchestratorAgent
from .agent_coordinator import AgentCoordinator, CoordinationResult
from .result_aggregator import ResultAggregator, AggregatedResult
from .pipeline_manager import PipelineManager, Pipeline, PipelineStage

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
