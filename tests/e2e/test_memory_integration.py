"""
End-to-end tests for memory integration.

Tests complete memory workflows including storage, retrieval,
semantic search, and cross-session persistence.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import asyncio
import hashlib
import json


class MemoryCategory(Enum):
    """Categories of memory."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"


class StorageBackend(Enum):
    """Storage backend types."""
    IN_MEMORY = "in_memory"
    FILE = "file"
    DATABASE = "database"
    VECTOR_DB = "vector_db"


class MemoryPriority(Enum):
    """Memory retention priority."""
    EPHEMERAL = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    PERMANENT = 4


@dataclass
class MemoryMetadata:
    """Metadata for a memory entry."""
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    source: str = "user"
    tags: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)


@dataclass
class MemoryEntry:
    """A memory entry with content and metadata."""
    id: str
    content: str
    category: MemoryCategory
    priority: MemoryPriority = MemoryPriority.NORMAL
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
    embedding: Optional[list[float]] = None
    summary: Optional[str] = None

    def update_access(self) -> None:
        """Update access tracking."""
        self.metadata.accessed_at = datetime.now()
        self.metadata.access_count += 1


@dataclass
class SearchResult:
    """A memory search result with relevance score."""
    entry: MemoryEntry
    score: float
    matched_terms: list[str] = field(default_factory=list)


class MockEmbeddingService:
    """Mock embedding service for vector operations."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._cache: dict[str, list[float]] = {}

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        if text in self._cache:
            return self._cache[text]

        # Deterministic mock embedding
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = [
            (b / 255.0) * 2 - 1
            for b in hash_bytes[:self.dimension]
        ]
        # Pad if needed
        while len(embedding) < self.dimension:
            embedding.append(0.0)

        self._cache[text] = embedding
        return embedding

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)


class MockStorageBackend:
    """Mock storage backend for persistence."""

    def __init__(self, backend_type: StorageBackend = StorageBackend.IN_MEMORY):
        self.backend_type = backend_type
        self._data: dict[str, dict] = {}
        self._snapshots: list[dict] = []

    async def save(self, key: str, value: dict) -> bool:
        """Save data to storage."""
        self._data[key] = value
        return True

    async def load(self, key: str) -> Optional[dict]:
        """Load data from storage."""
        return self._data.get(key)

    async def delete(self, key: str) -> bool:
        """Delete data from storage."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys with optional prefix filter."""
        return [k for k in self._data.keys() if k.startswith(prefix)]

    def create_snapshot(self) -> str:
        """Create a snapshot of current state."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "data": dict(self._data)
        }
        self._snapshots.append(snapshot)
        return f"snapshot-{len(self._snapshots)}"

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore from a snapshot."""
        idx = int(snapshot_id.split("-")[1]) - 1
        if 0 <= idx < len(self._snapshots):
            self._data = dict(self._snapshots[idx]["data"])
            return True
        return False


class MockMemoryStore:
    """Complete memory store with all operations."""

    def __init__(self):
        self.memories: dict[str, MemoryEntry] = {}
        self.embedding_service = MockEmbeddingService()
        self.storage = MockStorageBackend()
        self._indices: dict[MemoryCategory, list[str]] = {
            cat: [] for cat in MemoryCategory
        }

    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        # Generate embedding if not provided
        if entry.embedding is None:
            entry.embedding = await self.embedding_service.embed(entry.content)

        self.memories[entry.id] = entry
        self._indices[entry.category].append(entry.id)

        # Persist to storage
        await self.storage.save(
            f"memory:{entry.id}",
            self._serialize_entry(entry)
        )

        return True

    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID."""
        entry = self.memories.get(memory_id)
        if entry:
            entry.update_access()
        return entry

    async def search_semantic(
        self,
        query: str,
        category: Optional[MemoryCategory] = None,
        limit: int = 10
    ) -> list[SearchResult]:
        """Perform semantic search across memories."""
        query_embedding = await self.embedding_service.embed(query)
        results = []

        candidates = (
            self._indices.get(category, [])
            if category
            else list(self.memories.keys())
        )

        for memory_id in candidates:
            entry = self.memories.get(memory_id)
            if entry and entry.embedding:
                score = self.embedding_service.cosine_similarity(
                    query_embedding,
                    entry.embedding
                )
                results.append(SearchResult(entry=entry, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def search_keyword(
        self,
        keywords: list[str],
        category: Optional[MemoryCategory] = None
    ) -> list[SearchResult]:
        """Perform keyword search."""
        results = []
        candidates = (
            self._indices.get(category, [])
            if category
            else list(self.memories.keys())
        )

        for memory_id in candidates:
            entry = self.memories.get(memory_id)
            if entry:
                matched = [kw for kw in keywords if kw.lower() in entry.content.lower()]
                if matched:
                    score = len(matched) / len(keywords)
                    results.append(SearchResult(
                        entry=entry,
                        score=score,
                        matched_terms=matched
                    ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self.memories:
            entry = self.memories[memory_id]
            self._indices[entry.category].remove(memory_id)
            del self.memories[memory_id]
            await self.storage.delete(f"memory:{memory_id}")
            return True
        return False

    async def consolidate(self, category: MemoryCategory) -> list[MemoryEntry]:
        """Consolidate memories in a category."""
        memory_ids = self._indices.get(category, [])
        entries = [self.memories[mid] for mid in memory_ids if mid in self.memories]

        # Sort by access count and return top memories
        entries.sort(key=lambda e: e.metadata.access_count, reverse=True)
        return entries

    async def expire_old_memories(self, max_age_days: int = 30) -> int:
        """Expire memories older than threshold."""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        expired = 0

        to_delete = []
        for memory_id, entry in self.memories.items():
            if (entry.priority == MemoryPriority.EPHEMERAL and
                entry.metadata.accessed_at < cutoff):
                to_delete.append(memory_id)

        for memory_id in to_delete:
            await self.delete(memory_id)
            expired += 1

        return expired

    async def save_session(self, session_id: str) -> bool:
        """Save current session state."""
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "memories": [
                self._serialize_entry(e) for e in self.memories.values()
            ]
        }
        return await self.storage.save(f"session:{session_id}", session_data)

    async def restore_session(self, session_id: str) -> bool:
        """Restore session state."""
        session_data = await self.storage.load(f"session:{session_id}")
        if not session_data:
            return False

        for mem_data in session_data.get("memories", []):
            entry = self._deserialize_entry(mem_data)
            self.memories[entry.id] = entry
            self._indices[entry.category].append(entry.id)

        return True

    def _serialize_entry(self, entry: MemoryEntry) -> dict:
        """Serialize memory entry to dict."""
        return {
            "id": entry.id,
            "content": entry.content,
            "category": entry.category.value,
            "priority": entry.priority.value,
            "embedding": entry.embedding,
            "summary": entry.summary,
            "metadata": {
                "created_at": entry.metadata.created_at.isoformat(),
                "accessed_at": entry.metadata.accessed_at.isoformat(),
                "access_count": entry.metadata.access_count,
                "source": entry.metadata.source,
                "tags": entry.metadata.tags,
                "relationships": entry.metadata.relationships
            }
        }

    def _deserialize_entry(self, data: dict) -> MemoryEntry:
        """Deserialize dict to memory entry."""
        metadata = MemoryMetadata(
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            accessed_at=datetime.fromisoformat(data["metadata"]["accessed_at"]),
            access_count=data["metadata"]["access_count"],
            source=data["metadata"]["source"],
            tags=data["metadata"]["tags"],
            relationships=data["metadata"]["relationships"]
        )
        return MemoryEntry(
            id=data["id"],
            content=data["content"],
            category=MemoryCategory(data["category"]),
            priority=MemoryPriority(data["priority"]),
            embedding=data.get("embedding"),
            summary=data.get("summary"),
            metadata=metadata
        )


# ============================================================================
# Test Classes
# ============================================================================

class TestMemoryStorage:
    """Tests for memory storage operations."""

    @pytest.fixture
    def store(self) -> MockMemoryStore:
        """Create memory store."""
        return MockMemoryStore()

    @pytest.mark.asyncio
    async def test_store_memory(self, store: MockMemoryStore):
        """Test storing a memory."""
        entry = MemoryEntry(
            id="mem-1",
            content="Python is a programming language",
            category=MemoryCategory.SEMANTIC
        )

        result = await store.store(entry)

        assert result is True
        assert "mem-1" in store.memories
        assert entry.embedding is not None

    @pytest.mark.asyncio
    async def test_retrieve_memory(self, store: MockMemoryStore):
        """Test retrieving a memory."""
        entry = MemoryEntry(
            id="mem-2",
            content="Test content",
            category=MemoryCategory.EPISODIC
        )
        await store.store(entry)

        retrieved = await store.retrieve("mem-2")

        assert retrieved is not None
        assert retrieved.content == "Test content"
        assert retrieved.metadata.access_count == 1


class TestSemanticSearch:
    """Tests for semantic search."""

    @pytest.fixture
    async def populated_store(self) -> MockMemoryStore:
        """Create store with test memories."""
        store = MockMemoryStore()

        memories = [
            MemoryEntry(id="m1", content="Python programming tutorial",
                       category=MemoryCategory.SEMANTIC),
            MemoryEntry(id="m2", content="JavaScript web development",
                       category=MemoryCategory.SEMANTIC),
            MemoryEntry(id="m3", content="Python data science with pandas",
                       category=MemoryCategory.SEMANTIC),
        ]

        for mem in memories:
            await store.store(mem)

        return store

    @pytest.mark.asyncio
    async def test_semantic_search(self, populated_store: MockMemoryStore):
        """Test semantic search returns results."""
        results = await populated_store.search_semantic("Python programming")

        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)

    @pytest.mark.asyncio
    async def test_search_with_category_filter(self, populated_store: MockMemoryStore):
        """Test search with category filter."""
        results = await populated_store.search_semantic(
            "programming",
            category=MemoryCategory.SEMANTIC
        )

        assert all(r.entry.category == MemoryCategory.SEMANTIC for r in results)


class TestKeywordSearch:
    """Tests for keyword search."""

    @pytest.fixture
    async def store(self) -> MockMemoryStore:
        """Create store with test data."""
        store = MockMemoryStore()
        await store.store(MemoryEntry(
            id="kw1",
            content="Machine learning with TensorFlow",
            category=MemoryCategory.SEMANTIC
        ))
        await store.store(MemoryEntry(
            id="kw2",
            content="Deep learning neural networks",
            category=MemoryCategory.SEMANTIC
        ))
        return store

    @pytest.mark.asyncio
    async def test_keyword_search(self, store: MockMemoryStore):
        """Test keyword search."""
        results = await store.search_keyword(["learning", "neural"])

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_keyword_match_tracking(self, store: MockMemoryStore):
        """Test matched keywords are tracked."""
        results = await store.search_keyword(["learning"])

        assert any("learning" in r.matched_terms for r in results)


class TestMemoryDeletion:
    """Tests for memory deletion."""

    @pytest.fixture
    async def store(self) -> MockMemoryStore:
        """Create store with test memory."""
        store = MockMemoryStore()
        await store.store(MemoryEntry(
            id="del-1",
            content="To be deleted",
            category=MemoryCategory.EPISODIC
        ))
        return store

    @pytest.mark.asyncio
    async def test_delete_memory(self, store: MockMemoryStore):
        """Test deleting a memory."""
        result = await store.delete("del-1")

        assert result is True
        assert "del-1" not in store.memories

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, store: MockMemoryStore):
        """Test deleting non-existent memory."""
        result = await store.delete("does-not-exist")

        assert result is False


class TestSessionPersistence:
    """Tests for session persistence."""

    @pytest.fixture
    async def store(self) -> MockMemoryStore:
        """Create store with memories."""
        store = MockMemoryStore()
        await store.store(MemoryEntry(
            id="sess-1",
            content="Session memory 1",
            category=MemoryCategory.WORKING
        ))
        await store.store(MemoryEntry(
            id="sess-2",
            content="Session memory 2",
            category=MemoryCategory.EPISODIC
        ))
        return store

    @pytest.mark.asyncio
    async def test_save_session(self, store: MockMemoryStore):
        """Test saving session state."""
        result = await store.save_session("session-abc")

        assert result is True
        data = await store.storage.load("session:session-abc")
        assert data is not None

    @pytest.mark.asyncio
    async def test_restore_session(self, store: MockMemoryStore):
        """Test restoring session state."""
        await store.save_session("session-restore")

        # Clear and restore
        new_store = MockMemoryStore()
        new_store.storage = store.storage

        result = await new_store.restore_session("session-restore")

        assert result is True
        assert "sess-1" in new_store.memories


class TestMemoryConsolidation:
    """Tests for memory consolidation."""

    @pytest.fixture
    async def store(self) -> MockMemoryStore:
        """Create store with memories of varying access."""
        store = MockMemoryStore()

        m1 = MemoryEntry(id="c1", content="Rarely accessed",
                        category=MemoryCategory.SEMANTIC)
        m2 = MemoryEntry(id="c2", content="Frequently accessed",
                        category=MemoryCategory.SEMANTIC)
        m2.metadata.access_count = 100

        await store.store(m1)
        await store.store(m2)

        return store

    @pytest.mark.asyncio
    async def test_consolidate_returns_sorted(self, store: MockMemoryStore):
        """Test consolidation returns by access count."""
        results = await store.consolidate(MemoryCategory.SEMANTIC)

        assert len(results) == 2
        assert results[0].id == "c2"  # Most accessed first


class TestMemoryExpiration:
    """Tests for memory expiration."""

    @pytest.fixture
    async def store(self) -> MockMemoryStore:
        """Create store with old ephemeral memories."""
        store = MockMemoryStore()

        old_entry = MemoryEntry(
            id="old-1",
            content="Old memory",
            category=MemoryCategory.WORKING,
            priority=MemoryPriority.EPHEMERAL
        )
        old_entry.metadata.accessed_at = datetime.now() - timedelta(days=60)
        await store.store(old_entry)

        new_entry = MemoryEntry(
            id="new-1",
            content="New memory",
            category=MemoryCategory.WORKING,
            priority=MemoryPriority.EPHEMERAL
        )
        await store.store(new_entry)

        return store

    @pytest.mark.asyncio
    async def test_expire_old_memories(self, store: MockMemoryStore):
        """Test expiring old memories."""
        expired = await store.expire_old_memories(max_age_days=30)

        assert expired == 1
        assert "old-1" not in store.memories
        assert "new-1" in store.memories


class TestStorageBackend:
    """Tests for storage backend operations."""

    @pytest.fixture
    def backend(self) -> MockStorageBackend:
        """Create storage backend."""
        return MockStorageBackend()

    @pytest.mark.asyncio
    async def test_save_and_load(self, backend: MockStorageBackend):
        """Test saving and loading data."""
        await backend.save("key1", {"value": "test"})

        result = await backend.load("key1")

        assert result == {"value": "test"}

    def test_snapshots(self, backend: MockStorageBackend):
        """Test snapshot creation and restoration."""
        backend._data["initial"] = {"state": 1}

        snapshot_id = backend.create_snapshot()

        backend._data["initial"] = {"state": 2}
        backend.restore_snapshot(snapshot_id)

        assert backend._data["initial"]["state"] == 1
