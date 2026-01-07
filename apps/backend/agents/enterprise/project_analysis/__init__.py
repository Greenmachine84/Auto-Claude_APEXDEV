"""Project Analysis Module for enterprise agents.

Provides project structure and architecture analysis capabilities.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from .project_analyzer_agent import ProjectAnalyzerAgent
from .dependency_mapper import DependencyMapper, DependencyGraph
from .architecture_extractor import ArchitectureExtractor, ArchitectureMap
from .tech_debt_analyzer import TechDebtAnalyzer, TechDebtReport

__all__ = [
    # Agent
    "ProjectAnalyzerAgent",
    # Dependencies
    "DependencyMapper",
    "DependencyGraph",
    # Architecture
    "ArchitectureExtractor",
    "ArchitectureMap",
    # Tech Debt
    "TechDebtAnalyzer",
    "TechDebtReport",
]
