"""Semantic search engine combining vector and graph search.

Part of Phase 2: Memory System Architecture
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .knowledge_graph import KGNode, KnowledgeGraph
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class SemanticSearchResult:
    """Combined search result from vector and graph search."""

    id: str
    content: str
    score: float
    source: str  # "vector" or "graph" or "hybrid"
    related_nodes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SemanticSearchEngine:
    """Hybrid semantic search combining vector similarity and graph traversal."""

    def __init__(
        self,
        vector_store: VectorStore,
        knowledge_graph: KnowledgeGraph | None = None,
        embed_fn: Callable[[str], list[float]] | None = None,
    ):
        self._vector_store = vector_store
        self._kg = knowledge_graph
        self._embed_fn = embed_fn

    def search(
        self,
        query: str,
        k: int = 10,
        namespace: str = "default",
        include_graph: bool = True,
        graph_depth: int = 2,
    ) -> list[SemanticSearchResult]:
        results: list[SemanticSearchResult] = []

        # Vector search
        if self._embed_fn:
            query_vector = self._embed_fn(query)
            vector_results = self._vector_store.search(
                query_vector, k=k, namespace=namespace
            )
            for vr in vector_results:
                results.append(
                    SemanticSearchResult(
                        id=vr.entry.id,
                        content=vr.entry.content,
                        score=vr.score,
                        source="vector",
                        metadata=vr.entry.metadata,
                    )
                )

        # Graph expansion
        if include_graph and self._kg and results:
            top_ids = [r.id for r in results[:3]]
            for result in results:
                if result.id in top_ids:
                    traversal = self._kg.traverse(result.id, max_depth=graph_depth)
                    result.related_nodes = list(traversal["nodes"] - {result.id})
                    result.source = "hybrid"

        return results[:k]

    def search_by_vector(
        self, query_vector: list[float], k: int = 10, namespace: str = "default"
    ) -> list[SemanticSearchResult]:
        vector_results = self._vector_store.search(
            query_vector, k=k, namespace=namespace
        )
        return [
            SemanticSearchResult(
                id=vr.entry.id,
                content=vr.entry.content,
                score=vr.score,
                source="vector",
                metadata=vr.entry.metadata,
            )
            for vr in vector_results
        ]

    def find_related(self, node_id: str, max_depth: int = 2) -> list[KGNode]:
        if not self._kg:
            return []
        traversal = self._kg.traverse(node_id, max_depth=max_depth)
        return [
            self._kg.get_node(nid)
            for nid in traversal["nodes"]
            if nid != node_id and self._kg.get_node(nid)
        ]
