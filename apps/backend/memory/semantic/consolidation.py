"""Knowledge consolidation for semantic memory optimization.

Part of Phase 2: Memory System Architecture
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from .knowledge_graph import KGNode, KnowledgeGraph
from .vector_store import VectorEntry, VectorStore

logger = logging.getLogger(__name__)


@dataclass
class ConsolidationResult:
    """Result of a consolidation operation."""

    merged_nodes: int = 0
    new_edges: int = 0
    deduplicated: int = 0
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)


class KnowledgeConsolidator:
    """Consolidate and optimize semantic memory."""

    def __init__(
        self,
        vector_store: VectorStore,
        knowledge_graph: KnowledgeGraph,
        similarity_threshold: float = 0.85,
        embed_fn: Callable[[str], list[float]] | None = None,
    ):
        self._vector_store = vector_store
        self._kg = knowledge_graph
        self._threshold = similarity_threshold
        self._embed_fn = embed_fn

    def consolidate(self, namespace: str = "default") -> ConsolidationResult:
        start = datetime.utcnow()
        result = ConsolidationResult()

        try:
            # Find similar entries
            duplicates = self._find_duplicates(namespace)
            result.deduplicated = len(duplicates)

            # Merge similar nodes
            merged = self._merge_similar_nodes()
            result.merged_nodes = merged

            # Create relationship edges
            new_edges = self._infer_relationships(namespace)
            result.new_edges = new_edges

        except Exception as e:
            result.errors.append(str(e))
            logger.error("Consolidation error: %s", e)

        result.duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        return result

    def _find_duplicates(self, namespace: str) -> list[tuple[str, str]]:
        # Simplified duplicate detection
        duplicates: list[tuple[str, str]] = []
        # In production, would iterate through vectors and compare
        return duplicates

    def _merge_similar_nodes(self) -> int:
        # Merge nodes with high similarity
        merged = 0
        # In production, would query similar nodes and merge properties
        return merged

    def _infer_relationships(self, namespace: str) -> int:
        new_edges = 0
        # Infer relationships based on co-occurrence and similarity
        return new_edges

    def deduplicate_entry(self, entry: VectorEntry) -> str | None:
        """Check if entry is duplicate, return existing ID if so."""
        similar = self._vector_store.search(
            entry.vector, k=5, namespace=entry.namespace
        )
        for result in similar:
            if result.score >= self._threshold and result.entry.id != entry.id:
                logger.info(
                    "Dedup: %s matches %s (score=%.3f)",
                    entry.id,
                    result.entry.id,
                    result.score,
                )
                return result.entry.id
        return None

    def link_to_graph(self, entry: VectorEntry, node_type: str = "concept") -> str:
        """Create a graph node for a vector entry."""
        node = KGNode(
            id=entry.id,
            node_type=node_type,
            name=entry.content[:100],
            properties=entry.metadata,
            embedding=entry.vector,
        )
        self._kg.add_node(node)
        return node.id
