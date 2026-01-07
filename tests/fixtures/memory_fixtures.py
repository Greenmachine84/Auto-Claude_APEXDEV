"""
Memory test fixtures.

Provides reusable fixtures for testing memory systems including
stores, entries, embeddings, and persistence.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock
import hashlib
import pytest


class MemoryType(Enum):
    """Types of memory storage."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"


class MemoryTier(Enum):
    """Memory storage tiers."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class PersistenceBackend(Enum):
    """Persistence backend types."""
    IN_MEMORY = "in_memory"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    VECTOR_DB = "vector_db"


@dataclass
class MemoryMetadata:
    """Metadata for memory entries."""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    source: str = "test"
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)


@dataclass
class MemoryEntry:
    """A memory entry for testing."""
    id: str
    content: str
    memory_type: MemoryType = MemoryType.SEMANTIC
    tier: MemoryTier = MemoryTier.HOT
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
    embedding: Optional[list[float]] = None
    summary: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "tier": self.tier.value,
            "embedding": self.embedding,
            "summary": self.summary,
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "access_count": self.metadata.access_count,
                "tags": self.metadata.tags,
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        """Create from dictionary."""
        metadata = MemoryMetadata(
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            access_count=data["metadata"]["access_count"],
            tags=data["metadata"]["tags"]
        )
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            tier=MemoryTier(data["tier"]),
            embedding=data.get("embedding"),
            summary=data.get("summary"),
            metadata=metadata
        )


@dataclass
class MemoryTestContext:
    """Test context for memory operations."""
    store: Any
    entries: list[MemoryEntry] = field(default_factory=list)
    operations: list[dict] = field(default_factory=list)
    search_results: list[dict] = field(default_factory=list)

    def record_operation(self, operation: str, **kwargs) -> None:
        """Record a memory operation."""
        self.operations.append({
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        })


class MockEmbeddingGenerator:
    """Mock embedding generator for testing."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._cache: dict[str, list[float]] = {}

    def generate(self, text: str) -> list[float]:
        """Generate a deterministic embedding for text."""
        if text in self._cache:
            return self._cache[text]

        # Create deterministic embedding from hash
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = [(b / 255.0) * 2 - 1 for b in hash_bytes]

        # Pad to dimension
        while len(embedding) < self.dimension:
            embedding.extend(embedding[:self.dimension - len(embedding)])
        embedding = embedding[:self.dimension]

        self._cache[text] = embedding
        return embedding

    async def embed_async(self, text: str) -> list[float]:
        """Async version of generate."""
        return self.generate(text)

    def similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class MockMemoryStore:
    """Mock memory store for testing."""

    def __init__(self, backend: PersistenceBackend = PersistenceBackend.IN_MEMORY):
        self.backend = backend
        self.memories: dict[str, MemoryEntry] = {}
        self.embedding_generator = MockEmbeddingGenerator()
        self._indices: dict[MemoryType, list[str]] = {t: [] for t in MemoryType}

    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        if entry.embedding is None:
            entry.embedding = self.embedding_generator.generate(entry.content)

        self.memories[entry.id] = entry
        self._indices[entry.memory_type].append(entry.id)
        return True

    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID."""
        entry = self.memories.get(memory_id)
        if entry:
            entry.metadata.accessed_at = datetime.now()
            entry.metadata.access_count += 1
        return entry

    async def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> list[tuple[MemoryEntry, float]]:
        """Search memories semantically."""
        query_embedding = self.embedding_generator.generate(query)
        results = []

        candidates = (
            self._indices.get(memory_type, [])
            if memory_type
            else list(self.memories.keys())
        )

        for memory_id in candidates:
            entry = self.memories.get(memory_id)
            if entry and entry.embedding:
                score = self.embedding_generator.similarity(
                    query_embedding, entry.embedding
                )
                results.append((entry, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self.memories:
            entry = self.memories[memory_id]
            self._indices[entry.memory_type].remove(memory_id)
            del self.memories[memory_id]
            return True
        return False

    async def clear(self) -> int:
        """Clear all memories."""
        count = len(self.memories)
        self.memories.clear()
        for type_list in self._indices.values():
            type_list.clear()
        return count


def create_memory_entry(
    memory_id: str = None,
    content: str = "Test memory content",
    memory_type: MemoryType = MemoryType.SEMANTIC,
    **kwargs
) -> MemoryEntry:
    """Create a memory entry for testing."""
    if memory_id is None:
        memory_id = f"mem-{datetime.now().timestamp()}"

    return MemoryEntry(
        id=memory_id,
        content=content,
        memory_type=memory_type,
        **kwargs
    )


def create_memory_store(
    backend: PersistenceBackend = PersistenceBackend.IN_MEMORY
) -> MockMemoryStore:
    """Create a memory store for testing."""
    return MockMemoryStore(backend=backend)


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def memory_store() -> MockMemoryStore:
    """Provide a clean memory store."""
    return MockMemoryStore()


@pytest.fixture
def embedding_generator() -> MockEmbeddingGenerator:
    """Provide an embedding generator."""
    return MockEmbeddingGenerator()


@pytest.fixture
def sample_memories() -> list[MemoryEntry]:
    """Provide sample memory entries."""
    return [
        create_memory_entry(
            memory_id="mem-1",
            content="Python is a programming language",
            memory_type=MemoryType.SEMANTIC,
            tier=MemoryTier.HOT
        ),
        create_memory_entry(
            memory_id="mem-2",
            content="Machine learning with TensorFlow",
            memory_type=MemoryType.SEMANTIC,
            tier=MemoryTier.WARM
        ),
        create_memory_entry(
            memory_id="mem-3",
            content="User asked about code review",
            memory_type=MemoryType.EPISODIC,
            tier=MemoryTier.HOT
        ),
    ]


@pytest.fixture
async def populated_memory_store(
    memory_store: MockMemoryStore,
    sample_memories: list[MemoryEntry]
) -> MockMemoryStore:
    """Provide a memory store with sample data."""
    for entry in sample_memories:
        await memory_store.store(entry)
    return memory_store


@pytest.fixture
def memory_context(memory_store: MockMemoryStore) -> MemoryTestContext:
    """Provide a memory test context."""
    return MemoryTestContext(store=memory_store)


@pytest.fixture
def old_memory_entry() -> MemoryEntry:
    """Provide an old memory entry for expiration tests."""
    entry = create_memory_entry(
        memory_id="old-mem",
        content="Old memory content",
        tier=MemoryTier.COLD
    )
    entry.metadata.created_at = datetime.now() - timedelta(days=90)
    entry.metadata.accessed_at = datetime.now() - timedelta(days=60)
    return entry
