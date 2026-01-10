"""Vector storage abstraction for semantic memory.

Part of Phase 2: Memory System Architecture
"""

import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VectorEntry:
    """A vector entry in the store."""

    id: str
    vector: list[float]
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    namespace: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "vector": self.vector,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "namespace": self.namespace,
        }


@dataclass
class VectorSearchResult:
    """Result of a vector search."""

    entry: VectorEntry
    score: float
    distance: float = 0.0


class VectorStore(ABC):
    """Abstract vector storage interface."""

    @abstractmethod
    def store(self, entry: VectorEntry) -> str:
        pass

    @abstractmethod
    def search(
        self, query_vector: list[float], k: int = 10, namespace: str = "default"
    ) -> list[VectorSearchResult]:
        pass

    @abstractmethod
    def get(self, entry_id: str) -> VectorEntry | None:
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        pass


class SQLiteVectorStore(VectorStore):
    """SQLite-based vector store with brute-force similarity."""

    def __init__(self, db_path: str):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                vector TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                namespace TEXT DEFAULT 'default'
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_vectors_ns ON vectors(namespace)"
        )
        self._conn.commit()

    def store(self, entry: VectorEntry) -> str:
        self._conn.execute(
            "INSERT OR REPLACE INTO vectors (id, vector, content, metadata, created_at, namespace) VALUES (?, ?, ?, ?, ?, ?)",
            (
                entry.id,
                json.dumps(entry.vector),
                entry.content,
                json.dumps(entry.metadata),
                entry.created_at,
                entry.namespace,
            ),
        )
        self._conn.commit()
        return entry.id

    def search(
        self, query_vector: list[float], k: int = 10, namespace: str = "default"
    ) -> list[VectorSearchResult]:
        rows = self._conn.execute(
            "SELECT id, vector, content, metadata, created_at, namespace FROM vectors WHERE namespace = ?",
            (namespace,),
        ).fetchall()

        results = []
        for row in rows:
            stored_vector = json.loads(row[1])
            score = self._cosine_similarity(query_vector, stored_vector)
            entry = VectorEntry(
                id=row[0],
                vector=stored_vector,
                content=row[2],
                metadata=json.loads(row[3] or "{}"),
                created_at=row[4],
                namespace=row[5],
            )
            results.append(
                VectorSearchResult(entry=entry, score=score, distance=1 - score)
            )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    def get(self, entry_id: str) -> VectorEntry | None:
        row = self._conn.execute(
            "SELECT * FROM vectors WHERE id = ?", (entry_id,)
        ).fetchone()
        if not row:
            return None
        return VectorEntry(
            id=row[0],
            vector=json.loads(row[1]),
            content=row[2],
            metadata=json.loads(row[3] or "{}"),
            created_at=row[4],
            namespace=row[5],
        )

    def delete(self, entry_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM vectors WHERE id = ?", (entry_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
