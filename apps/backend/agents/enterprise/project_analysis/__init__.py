"""Project Analysis Module for enterprise agents.

Provides project structure and architecture analysis capabilities.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from .architecture_extractor import ArchitectureExtractor, ArchitectureMap
from .dependency_mapper import DependencyGraph, DependencyMapper
from .project_analyzer_agent import ProjectAnalyzerAgent
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
