# Memory API Reference

Complete API documentation for the Auto-Claude memory system.

## Overview

The Memory API provides interfaces for storing, retrieving, and searching
memories across agent sessions with support for semantic search.

## Memory Categories

| Category | Description | Retention |
|----------|-------------|-----------|
| `EPISODIC` | Event-based memories | Session-based |
| `SEMANTIC` | Factual knowledge | Long-term |
| `PROCEDURAL` | How-to knowledge | Permanent |
| `WORKING` | Active context | Temporary |

## Core Classes

### MemoryStore

Primary interface for memory operations.

```python
from apps.backend.memory import MemoryStore

store = MemoryStore(
    backend="vector_db",
    embedding_model="text-embedding-3-small"
)
```

#### Methods

##### store

Store a new memory entry.

```python
entry = MemoryEntry(
    id="mem-123",
    content="Python uses indentation for code blocks",
    category=MemoryCategory.SEMANTIC,
    priority=MemoryPriority.NORMAL,
    metadata=MemoryMetadata(
        source="documentation",
        tags=["python", "syntax"]
    )
)

success = await store.store(entry)
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry` | `MemoryEntry` | Yes | Memory to store |

##### retrieve

Retrieve a memory by ID.

```python
memory = await store.retrieve("mem-123")
if memory:
    print(f"Content: {memory.content}")
    print(f"Accessed {memory.metadata.access_count} times")
```

##### search_semantic

Perform semantic similarity search.

```python
results = await store.search_semantic(
    query="How does Python handle indentation?",
    category=MemoryCategory.SEMANTIC,
    limit=10,
    threshold=0.7
)

for result in results:
    print(f"Score: {result.score:.2f} - {result.entry.content[:50]}")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | Search query |
| `category` | `MemoryCategory` | `None` | Filter by category |
| `limit` | `int` | `10` | Max results |
| `threshold` | `float` | `0.0` | Min similarity score |

##### search_keyword

Perform keyword-based search.

```python
results = await store.search_keyword(
    keywords=["python", "indentation"],
    category=MemoryCategory.SEMANTIC,
    match_all=False
)
```

##### delete

Delete a memory by ID.

```python
deleted = await store.delete("mem-123")
```

### MemoryEntry

Represents a single memory.

```python
@dataclass
class MemoryEntry:
    id: str
    content: str
    category: MemoryCategory
    priority: MemoryPriority = MemoryPriority.NORMAL
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
    embedding: Optional[list[float]] = None
    summary: Optional[str] = None
```

### MemoryMetadata

Metadata associated with a memory.

```python
@dataclass
class MemoryMetadata:
    created_at: datetime
    accessed_at: datetime
    access_count: int
    source: str
    tags: list[str]
    relationships: list[str]
```

## Memory Priority

| Priority | Value | Description |
|----------|-------|-------------|
| `EPHEMERAL` | 0 | Deleted after session |
| `LOW` | 1 | May be consolidated |
| `NORMAL` | 2 | Standard retention |
| `HIGH` | 3 | Protected from cleanup |
| `PERMANENT` | 4 | Never deleted |

## Session Management

### Save Session

```python
await store.save_session("session-abc")
```

### Restore Session

```python
await store.restore_session("session-abc")
```

### Session Data

```python
session_data = await store.get_session_data("session-abc")
print(f"Memories: {len(session_data.memories)}")
print(f"Created: {session_data.created_at}")
```

## Memory Consolidation

Optimize memory storage by consolidating similar entries.

```python
# Consolidate memories in a category
consolidated = await store.consolidate(
    category=MemoryCategory.SEMANTIC,
    strategy="merge_similar",
    threshold=0.9
)

print(f"Consolidated {len(consolidated)} memories")
```

### Consolidation Strategies

| Strategy | Description |
|----------|-------------|
| `merge_similar` | Merge highly similar memories |
| `summarize` | Create summary of related memories |
| `prune_duplicates` | Remove exact duplicates |

## Memory Expiration

Configure automatic cleanup of old memories.

```python
# Expire memories older than 30 days
expired_count = await store.expire_old_memories(
    max_age_days=30,
    priority_threshold=MemoryPriority.LOW
)

print(f"Expired {expired_count} memories")
```

## Storage Backends

### In-Memory

Fast, non-persistent storage for development.

```python
store = MemoryStore(backend="in_memory")
```

### File System

Persistent file-based storage.

```python
store = MemoryStore(
    backend="file",
    config={"path": "./data/memories"}
)
```

### Vector Database

Production vector storage with semantic search.

```python
store = MemoryStore(
    backend="vector_db",
    config={
        "provider": "chromadb",
        "collection": "agent_memories"
    }
)
```

## Embedding Configuration

Configure the embedding model for semantic search.

```python
store = MemoryStore(
    embedding_config=EmbeddingConfig(
        provider="openai",
        model="text-embedding-3-small",
        dimension=1536,
        batch_size=100
    )
)
```

## Events

Subscribe to memory events.

```python
@store.on("memory.stored")
async def on_stored(event):
    print(f"Stored: {event.memory_id}")

@store.on("memory.accessed")
async def on_accessed(event):
    print(f"Accessed: {event.memory_id}")

@store.on("memory.deleted")
async def on_deleted(event):
    print(f"Deleted: {event.memory_id}")
```

## Best Practices

1. **Choose appropriate categories** - Match memory type to content
2. **Set priorities wisely** - Protect important memories
3. **Use semantic search** - For natural language queries
4. **Regular consolidation** - Optimize storage periodically
5. **Monitor memory usage** - Track growth and cleanup

## See Also

- [Agent API](agent-api.md)
- [Memory Usage Guide](../guides/memory-usage.md)
- [Storage Configuration](../guides/configuration.md)
