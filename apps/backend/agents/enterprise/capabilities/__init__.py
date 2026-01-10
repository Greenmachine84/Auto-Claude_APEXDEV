"""Capabilities Module for enterprise agents.

Provides shared capabilities that can be used across agents.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from .code_analysis import AnalysisResult, CodeAnalysisCapability
from .collaboration import CollaborationCapability, Message
from .documentation import DocOutput, DocumentationCapability
from .test_generation import TestGenerationCapability, TestSuite

__all__ = [
    # Code Analysis
    "CodeAnalysisCapability",
    "AnalysisResult",
    # Test Generation
    "TestGenerationCapability",
    "TestSuite",
    # Documentation
    "DocumentationCapability",
    "DocOutput",
    # Collaboration
    "CollaborationCapability",
    "Message",
]
