"""Semantic memory module - Knowledge graph and vector storage.

Provides semantic memory capabilities:
- Vector storage with configurable backends
- Knowledge graph nodes and edges
- Semantic similarity search
- Knowledge consolidation

Part of Phase 2: Memory System Architecture
"""

from .vector_store import VectorStore, VectorEntry, VectorSearchResult
from .knowledge_graph import KnowledgeGraph, KGNode, KGEdge
from .semantic_search import SemanticSearchEngine
from .consolidation import KnowledgeConsolidator

__all__ = [
    "VectorStore",
    "VectorEntry",
    "VectorSearchResult",
    "KnowledgeGraph",
    "KGNode",
    "KGEdge",
    "SemanticSearchEngine",
    "KnowledgeConsolidator",
]
