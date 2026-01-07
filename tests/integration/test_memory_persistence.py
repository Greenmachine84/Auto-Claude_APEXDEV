"""
Integration tests for Memory Persistence.

Tests the complete flow of memory storage, retrieval, and persistence
across sessions, including episode storage, semantic search, and tiered memory.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock
import json


class MemoryTier(Enum):
    """Memory storage tiers."""
    SHORT_TERM = "short_term"
    WORKING = "working"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"


class MemoryType(Enum):
    """Types of memory entries."""
    EPISODE = "episode"
    FACT = "fact"
    SKILL = "skill"
    CONTEXT = "context"


@dataclass
class MemoryEntry:
    """A memory entry."""
    id: str
    content: str
    memory_type: MemoryType
    tier: MemoryTier
    embedding: list[float] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance_score: float = 0.5

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "tier": self.tier.value,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            tier=MemoryTier(data["tier"]),
            embedding=data.get("embedding", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            accessed_at=datetime.fromisoformat(data["accessed_at"]),
            access_count=data.get("access_count", 0),
            importance_score=data.get("importance_score", 0.5)
        )


@dataclass
class SearchResult:
    """Result from semantic search."""
    entry: MemoryEntry
    similarity_score: float
    rank: int


class MockEmbeddingService:
    """Mock embedding service for memory integration."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.call_count = 0
        self._embeddings: dict[str, list[float]] = {}

    def set_embedding(self, text: str, embedding: list[float]) -> None:
        """Set predefined embedding for text."""
        self._embeddings[text] = embedding

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        self.call_count += 1
        if text in self._embeddings:
            return self._embeddings[text]
        # Generate deterministic embedding based on text hash
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_val >> i & 0xFF) / 255.0 for i in range(self.dimension)]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return [await self.embed(text) for text in texts]


class MockPersistenceBackend:
    """Mock persistence backend for memory storage."""

    def __init__(self):
        self._storage: dict[str, str] = {}
        self.save_count = 0
        self.load_count = 0
        self._should_fail = False

    def set_failure_mode(self, should_fail: bool) -> None:
        """Configure failure behavior."""
        self._should_fail = should_fail

    async def save(self, key: str, data: str) -> bool:
        """Save data to storage."""
        self.save_count += 1
        if self._should_fail:
            raise IOError("Persistence backend failed")
        self._storage[key] = data
        return True

    async def load(self, key: str) -> Optional[str]:
        """Load data from storage."""
        self.load_count += 1
        if self._should_fail:
            raise IOError("Persistence backend failed")
        return self._storage.get(key)

    async def delete(self, key: str) -> bool:
        """Delete data from storage."""
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        """List keys with optional prefix filter."""
        return [k for k in self._storage.keys() if k.startswith(prefix)]

    async def clear(self) -> None:
        """Clear all storage."""
        self._storage.clear()


class MockMemoryStore:
    """Mock memory store with full persistence support."""

    def __init__(
        self,
        backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ):
        self.backend = backend
        self.embedding_service = embedding_service
        self._entries: dict[str, MemoryEntry] = {}
        self._tier_limits = {
            MemoryTier.SHORT_TERM: 100,
            MemoryTier.WORKING: 50,
            MemoryTier.LONG_TERM: 10000,
            MemoryTier.EPISODIC: 1000
        }

    async def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry."""
        if not entry.embedding:
            entry.embedding = await self.embedding_service.embed(entry.content)
        self._entries[entry.id] = entry
        return entry.id

    async def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.accessed_at = datetime.now()
            entry.access_count += 1
        return entry

    async def search(
        self,
        query: str,
        limit: int = 10,
        tier: Optional[MemoryTier] = None,
        memory_type: Optional[MemoryType] = None
    ) -> list[SearchResult]:
        """Search for similar memories."""
        query_embedding = await self.embedding_service.embed(query)

        results = []
        for entry in self._entries.values():
            if tier and entry.tier != tier:
                continue
            if memory_type and entry.memory_type != memory_type:
                continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, entry.embedding)
            results.append(SearchResult(
                entry=entry,
                similarity_score=similarity,
                rank=0
            ))

        # Sort by similarity and assign ranks
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        for i, result in enumerate(results[:limit]):
            result.rank = i + 1

        return results[:limit]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b) or not a:
            return 0.0
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def persist(self) -> bool:
        """Persist all entries to backend."""
        data = {
            entry_id: entry.to_dict()
            for entry_id, entry in self._entries.items()
        }
        await self.backend.save("memory_store", json.dumps(data))
        return True

    async def restore(self) -> bool:
        """Restore entries from backend."""
        data_str = await self.backend.load("memory_store")
        if data_str:
            data = json.loads(data_str)
            self._entries = {
                entry_id: MemoryEntry.from_dict(entry_data)
                for entry_id, entry_data in data.items()
            }
            return True
        return False

    async def promote(self, entry_id: str, target_tier: MemoryTier) -> bool:
        """Promote entry to higher tier."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.tier = target_tier
            return True
        return False

    async def get_by_tier(self, tier: MemoryTier) -> list[MemoryEntry]:
        """Get all entries in a tier."""
        return [e for e in self._entries.values() if e.tier == tier]

    async def cleanup_tier(self, tier: MemoryTier) -> int:
        """Remove oldest entries if tier exceeds limit."""
        tier_entries = await self.get_by_tier(tier)
        limit = self._tier_limits[tier]

        if len(tier_entries) <= limit:
            return 0

        # Sort by importance and access time
        tier_entries.sort(
            key=lambda e: (e.importance_score, e.accessed_at)
        )

        remove_count = len(tier_entries) - limit
        removed = 0
        for entry in tier_entries[:remove_count]:
            del self._entries[entry.id]
            removed += 1

        return removed


# ============================================================================
# Test Classes
# ============================================================================

class TestMemoryPersistence:
    """Tests for memory persistence to backend."""

    @pytest.fixture
    def backend(self) -> MockPersistenceBackend:
        """Create persistence backend."""
        return MockPersistenceBackend()

    @pytest.fixture
    def embedding_service(self) -> MockEmbeddingService:
        """Create embedding service."""
        return MockEmbeddingService()

    @pytest.fixture
    def store(
        self,
        backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ) -> MockMemoryStore:
        """Create memory store."""
        return MockMemoryStore(backend, embedding_service)

    @pytest.mark.asyncio
    async def test_persist_and_restore(self, store: MockMemoryStore):
        """Test persisting and restoring memories."""
        entry = MemoryEntry(
            id="test-1",
            content="Test memory content",
            memory_type=MemoryType.EPISODE,
            tier=MemoryTier.SHORT_TERM
        )
        await store.store(entry)
        await store.persist()

        # Clear in-memory entries
        store._entries.clear()
        assert len(store._entries) == 0

        # Restore
        await store.restore()
        assert len(store._entries) == 1
        restored = await store.retrieve("test-1")
        assert restored is not None
        assert restored.content == "Test memory content"

    @pytest.mark.asyncio
    async def test_persist_multiple_entries(self, store: MockMemoryStore):
        """Test persisting multiple entries."""
        for i in range(10):
            entry = MemoryEntry(
                id=f"entry-{i}",
                content=f"Content {i}",
                memory_type=MemoryType.FACT,
                tier=MemoryTier.LONG_TERM
            )
            await store.store(entry)

        await store.persist()
        store._entries.clear()
        await store.restore()

        assert len(store._entries) == 10

    @pytest.mark.asyncio
    async def test_persistence_failure_handling(
        self,
        store: MockMemoryStore,
        backend: MockPersistenceBackend
    ):
        """Test handling of persistence failures."""
        entry = MemoryEntry(
            id="test-1",
            content="Test content",
            memory_type=MemoryType.EPISODE,
            tier=MemoryTier.SHORT_TERM
        )
        await store.store(entry)

        backend.set_failure_mode(True)

        with pytest.raises(IOError):
            await store.persist()


class TestSemanticSearch:
    """Tests for semantic search across memories."""

    @pytest.fixture
    def backend(self) -> MockPersistenceBackend:
        """Create persistence backend."""
        return MockPersistenceBackend()

    @pytest.fixture
    def embedding_service(self) -> MockEmbeddingService:
        """Create embedding service with predefined embeddings."""
        service = MockEmbeddingService(dimension=3)
        service.set_embedding("python programming", [1.0, 0.0, 0.0])
        service.set_embedding("javascript coding", [0.9, 0.1, 0.0])
        service.set_embedding("cooking recipes", [0.0, 0.0, 1.0])
        service.set_embedding("python code", [0.95, 0.05, 0.0])
        return service

    @pytest.fixture
    def store(
        self,
        backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ) -> MockMemoryStore:
        """Create memory store."""
        return MockMemoryStore(backend, embedding_service)

    @pytest.mark.asyncio
    async def test_search_returns_similar(self, store: MockMemoryStore):
        """Test search returns similar entries."""
        # Store entries with different topics
        await store.store(MemoryEntry(
            id="py-1",
            content="python programming",
            memory_type=MemoryType.SKILL,
            tier=MemoryTier.LONG_TERM
        ))
        await store.store(MemoryEntry(
            id="js-1",
            content="javascript coding",
            memory_type=MemoryType.SKILL,
            tier=MemoryTier.LONG_TERM
        ))
        await store.store(MemoryEntry(
            id="cook-1",
            content="cooking recipes",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.LONG_TERM
        ))

        results = await store.search("python code", limit=2)

        assert len(results) == 2
        assert results[0].entry.id == "py-1"
        assert results[0].similarity_score > 0.9

    @pytest.mark.asyncio
    async def test_search_with_tier_filter(self, store: MockMemoryStore):
        """Test search with tier filter."""
        await store.store(MemoryEntry(
            id="st-1",
            content="python programming",
            memory_type=MemoryType.SKILL,
            tier=MemoryTier.SHORT_TERM
        ))
        await store.store(MemoryEntry(
            id="lt-1",
            content="python programming",
            memory_type=MemoryType.SKILL,
            tier=MemoryTier.LONG_TERM
        ))

        results = await store.search(
            "python programming",
            tier=MemoryTier.LONG_TERM
        )

        assert len(results) == 1
        assert results[0].entry.tier == MemoryTier.LONG_TERM

    @pytest.mark.asyncio
    async def test_search_with_type_filter(self, store: MockMemoryStore):
        """Test search with memory type filter."""
        await store.store(MemoryEntry(
            id="skill-1",
            content="python programming",
            memory_type=MemoryType.SKILL,
            tier=MemoryTier.LONG_TERM
        ))
        await store.store(MemoryEntry(
            id="fact-1",
            content="python programming",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.LONG_TERM
        ))

        results = await store.search(
            "python programming",
            memory_type=MemoryType.SKILL
        )

        assert len(results) == 1
        assert results[0].entry.memory_type == MemoryType.SKILL


class TestTierManagement:
    """Tests for memory tier management."""

    @pytest.fixture
    def backend(self) -> MockPersistenceBackend:
        """Create persistence backend."""
        return MockPersistenceBackend()

    @pytest.fixture
    def embedding_service(self) -> MockEmbeddingService:
        """Create embedding service."""
        return MockEmbeddingService()

    @pytest.fixture
    def store(
        self,
        backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ) -> MockMemoryStore:
        """Create memory store with small limits."""
        store = MockMemoryStore(backend, embedding_service)
        store._tier_limits[MemoryTier.SHORT_TERM] = 5
        return store

    @pytest.mark.asyncio
    async def test_promote_entry(self, store: MockMemoryStore):
        """Test promoting entry to higher tier."""
        entry = MemoryEntry(
            id="promote-1",
            content="Important memory",
            memory_type=MemoryType.EPISODE,
            tier=MemoryTier.SHORT_TERM
        )
        await store.store(entry)

        await store.promote("promote-1", MemoryTier.LONG_TERM)

        retrieved = await store.retrieve("promote-1")
        assert retrieved.tier == MemoryTier.LONG_TERM

    @pytest.mark.asyncio
    async def test_get_by_tier(self, store: MockMemoryStore):
        """Test getting entries by tier."""
        for i in range(3):
            await store.store(MemoryEntry(
                id=f"st-{i}",
                content=f"Short term {i}",
                memory_type=MemoryType.CONTEXT,
                tier=MemoryTier.SHORT_TERM
            ))
        for i in range(2):
            await store.store(MemoryEntry(
                id=f"lt-{i}",
                content=f"Long term {i}",
                memory_type=MemoryType.FACT,
                tier=MemoryTier.LONG_TERM
            ))

        short_term = await store.get_by_tier(MemoryTier.SHORT_TERM)
        long_term = await store.get_by_tier(MemoryTier.LONG_TERM)

        assert len(short_term) == 3
        assert len(long_term) == 2

    @pytest.mark.asyncio
    async def test_tier_cleanup(self, store: MockMemoryStore):
        """Test cleanup removes oldest entries when tier exceeds limit."""
        # Fill short-term tier beyond limit
        for i in range(10):
            entry = MemoryEntry(
                id=f"st-{i}",
                content=f"Short term {i}",
                memory_type=MemoryType.CONTEXT,
                tier=MemoryTier.SHORT_TERM,
                importance_score=0.1 * i  # Increasing importance
            )
            await store.store(entry)

        removed = await store.cleanup_tier(MemoryTier.SHORT_TERM)

        assert removed == 5
        remaining = await store.get_by_tier(MemoryTier.SHORT_TERM)
        assert len(remaining) == 5
        # Higher importance entries should remain
        assert all(e.importance_score >= 0.5 for e in remaining)


class TestAccessTracking:
    """Tests for memory access tracking."""

    @pytest.fixture
    def backend(self) -> MockPersistenceBackend:
        """Create persistence backend."""
        return MockPersistenceBackend()

    @pytest.fixture
    def embedding_service(self) -> MockEmbeddingService:
        """Create embedding service."""
        return MockEmbeddingService()

    @pytest.fixture
    def store(
        self,
        backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ) -> MockMemoryStore:
        """Create memory store."""
        return MockMemoryStore(backend, embedding_service)

    @pytest.mark.asyncio
    async def test_access_count_incremented(self, store: MockMemoryStore):
        """Test access count is incremented on retrieval."""
        entry = MemoryEntry(
            id="access-test",
            content="Test content",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.LONG_TERM
        )
        await store.store(entry)

        for _ in range(5):
            await store.retrieve("access-test")

        retrieved = await store.retrieve("access-test")
        assert retrieved.access_count == 6

    @pytest.mark.asyncio
    async def test_accessed_at_updated(self, store: MockMemoryStore):
        """Test accessed_at is updated on retrieval."""
        entry = MemoryEntry(
            id="time-test",
            content="Test content",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.LONG_TERM
        )
        original_time = entry.accessed_at
        await store.store(entry)

        import asyncio
        await asyncio.sleep(0.01)

        retrieved = await store.retrieve("time-test")
        assert retrieved.accessed_at > original_time


class TestEmbeddingIntegration:
    """Tests for embedding service integration."""

    @pytest.fixture
    def backend(self) -> MockPersistenceBackend:
        """Create persistence backend."""
        return MockPersistenceBackend()

    @pytest.fixture
    def embedding_service(self) -> MockEmbeddingService:
        """Create embedding service."""
        return MockEmbeddingService()

    @pytest.fixture
    def store(
        self,
        backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ) -> MockMemoryStore:
        """Create memory store."""
        return MockMemoryStore(backend, embedding_service)

    @pytest.mark.asyncio
    async def test_embedding_generated_on_store(
        self,
        store: MockMemoryStore,
        embedding_service: MockEmbeddingService
    ):
        """Test embedding is generated when storing entry."""
        entry = MemoryEntry(
            id="embed-test",
            content="Test content",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.LONG_TERM
        )
        await store.store(entry)

        assert embedding_service.call_count == 1
        retrieved = await store.retrieve("embed-test")
        assert len(retrieved.embedding) == 384

    @pytest.mark.asyncio
    async def test_predefined_embedding_preserved(
        self,
        store: MockMemoryStore,
        embedding_service: MockEmbeddingService
    ):
        """Test predefined embedding is preserved."""
        entry = MemoryEntry(
            id="predef-embed",
            content="Test content",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.LONG_TERM,
            embedding=[1.0, 2.0, 3.0]
        )
        await store.store(entry)

        assert embedding_service.call_count == 0
        retrieved = await store.retrieve("predef-embed")
        assert retrieved.embedding == [1.0, 2.0, 3.0]


class TestCrossSessionPersistence:
    """Tests for persistence across simulated sessions."""

    @pytest.fixture
    def shared_backend(self) -> MockPersistenceBackend:
        """Create shared persistence backend."""
        return MockPersistenceBackend()

    @pytest.fixture
    def embedding_service(self) -> MockEmbeddingService:
        """Create embedding service."""
        return MockEmbeddingService()

    @pytest.mark.asyncio
    async def test_memories_survive_session(
        self,
        shared_backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ):
        """Test memories persist across sessions."""
        # Session 1: Create and persist
        store1 = MockMemoryStore(shared_backend, embedding_service)
        await store1.store(MemoryEntry(
            id="session-1-entry",
            content="Created in session 1",
            memory_type=MemoryType.EPISODE,
            tier=MemoryTier.LONG_TERM
        ))
        await store1.persist()

        # Session 2: Restore and verify
        store2 = MockMemoryStore(shared_backend, embedding_service)
        await store2.restore()

        retrieved = await store2.retrieve("session-1-entry")
        assert retrieved is not None
        assert retrieved.content == "Created in session 1"

    @pytest.mark.asyncio
    async def test_modifications_persist(
        self,
        shared_backend: MockPersistenceBackend,
        embedding_service: MockEmbeddingService
    ):
        """Test modifications persist across sessions."""
        # Session 1: Create entry
        store1 = MockMemoryStore(shared_backend, embedding_service)
        await store1.store(MemoryEntry(
            id="mod-test",
            content="Original content",
            memory_type=MemoryType.FACT,
            tier=MemoryTier.SHORT_TERM,
            importance_score=0.3
        ))
        await store1.persist()

        # Session 2: Modify and persist
        store2 = MockMemoryStore(shared_backend, embedding_service)
        await store2.restore()
        await store2.promote("mod-test", MemoryTier.LONG_TERM)
        entry = await store2.retrieve("mod-test")
        entry.importance_score = 0.9
        await store2.persist()

        # Session 3: Verify modifications
        store3 = MockMemoryStore(shared_backend, embedding_service)
        await store3.restore()

        retrieved = await store3.retrieve("mod-test")
        assert retrieved.tier == MemoryTier.LONG_TERM
        assert retrieved.importance_score == 0.9
