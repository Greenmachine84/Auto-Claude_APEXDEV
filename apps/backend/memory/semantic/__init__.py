"""Semantic memory module - Knowledge graph and vector storage.

Provides semantic memory capabilities:
- Vector storage with configurable backends
- Knowledge graph nodes and edges
- Semantic similarity search
- Knowledge consolidation

Part of Phase 2: Memory System Architecture
"""

from .consolidation import KnowledgeConsolidator
from .knowledge_graph import KGEdge, KGNode, KnowledgeGraph
from .semantic_search import SemanticSearchEngine
from .vector_store import VectorEntry, VectorSearchResult, VectorStore

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
