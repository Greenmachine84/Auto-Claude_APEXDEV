# Memory Management Guide

A comprehensive guide to using the Auto-Claude memory system.

## Overview

The memory system enables agents to retain and recall information across
sessions, supporting both semantic search and structured retrieval.

## Memory Categories

### Episodic Memory

Event-based memories tied to specific interactions.

```python
from apps.backend.memory import MemoryStore, MemoryEntry, MemoryCategory

# Store an episodic memory
await store.store(MemoryEntry(
    id="ep-001",
    content="User requested a Python function for data validation",
    category=MemoryCategory.EPISODIC,
    metadata=MemoryMetadata(
        source="user_request",
        tags=["python", "validation"],
        relationships=["task-123"]
    )
))
```

### Semantic Memory

Factual knowledge and learned information.

```python
await store.store(MemoryEntry(
    id="sem-001",
    content="Python's dataclasses module provides a decorator for creating classes with automatically generated __init__, __repr__, and other methods",
    category=MemoryCategory.SEMANTIC,
    priority=MemoryPriority.HIGH,
    metadata=MemoryMetadata(
        source="documentation",
        tags=["python", "dataclasses"]
    )
))
```

### Procedural Memory

How-to knowledge and procedures.

```python
await store.store(MemoryEntry(
    id="proc-001",
    content="""To create a REST API in FastAPI:
    1. Install FastAPI and uvicorn
    2. Create app instance with FastAPI()
    3. Define route handlers with decorators
    4. Run with uvicorn""",
    category=MemoryCategory.PROCEDURAL,
    priority=MemoryPriority.PERMANENT
))
```

### Working Memory

Active context for current task.

```python
await store.store(MemoryEntry(
    id="work-001",
    content="Current task: Implementing user authentication",
    category=MemoryCategory.WORKING,
    priority=MemoryPriority.EPHEMERAL  # Cleared after session
))
```

## Memory Operations

### Storing Memories

```python
from apps.backend.memory import MemoryStore, MemoryEntry

store = MemoryStore(backend="chromadb")

entry = MemoryEntry(
    id="unique-id",
    content="Content to remember",
    category=MemoryCategory.SEMANTIC,
    priority=MemoryPriority.NORMAL,
    metadata=MemoryMetadata(
        source="agent",
        tags=["tag1", "tag2"]
    )
)

success = await store.store(entry)
```

### Retrieving Memories

```python
# By ID
memory = await store.retrieve("unique-id")

# Semantic search
results = await store.search_semantic(
    query="How to create REST APIs in Python?",
    category=MemoryCategory.PROCEDURAL,
    limit=5,
    threshold=0.7
)

# Keyword search
results = await store.search_keyword(
    keywords=["python", "rest", "api"],
    match_all=False
)
```

### Updating Memories

```python
# Retrieve and modify
memory = await store.retrieve("mem-123")
memory.content = "Updated content"
memory.metadata.tags.append("updated")

# Re-store (updates if ID exists)
await store.store(memory)
```

### Deleting Memories

```python
# Single deletion
await store.delete("mem-123")

# Bulk deletion by filter
await store.delete_by_filter(
    category=MemoryCategory.WORKING,
    before=datetime.now() - timedelta(days=7)
)
```

## Storage Backends

### In-Memory Storage

Fast, non-persistent storage for development.

```python
store = MemoryStore(backend="in_memory")
```

**Pros**: Fast, no setup required
**Cons**: Data lost on restart

### File Storage

Simple file-based persistence.

```python
store = MemoryStore(
    backend="file",
    config={
        "path": "./data/memories",
        "format": "json"  # or "pickle"
    }
)
```

**Pros**: Simple, portable
**Cons**: Slower for large datasets

### ChromaDB (Vector Database)

Production vector storage with semantic search.

```python
store = MemoryStore(
    backend="chromadb",
    config={
        "persist_directory": "./data/chroma",
        "collection_name": "agent_memories"
    }
)
```

**Pros**: Fast semantic search, persistent
**Cons**: Requires more setup

### PostgreSQL with pgvector

Enterprise-grade vector storage.

```python
store = MemoryStore(
    backend="postgres",
    config={
        "connection_string": "postgresql://user:pass@localhost/db",
        "table_name": "memories"
    }
)
```

## Embedding Configuration

### OpenAI Embeddings

```python
store = MemoryStore(
    backend="chromadb",
    embedding_config=EmbeddingConfig(
        provider="openai",
        model="text-embedding-3-small",
        dimension=1536
    )
)
```

### Local Embeddings (Ollama)

```python
store = MemoryStore(
    backend="chromadb",
    embedding_config=EmbeddingConfig(
        provider="ollama",
        model="nomic-embed-text",
        base_url="http://localhost:11434"
    )
)
```

## Memory Lifecycle

### Session Management

```python
# Save session state
await store.save_session("session-123")

# Restore session state
await store.restore_session("session-123")

# Clear session memories
await store.clear_session("session-123")
```

### Memory Consolidation

Optimize storage by merging similar memories.

```python
# Consolidate semantic memories
consolidated = await store.consolidate(
    category=MemoryCategory.SEMANTIC,
    strategy="merge_similar",
    threshold=0.95
)

print(f"Merged {consolidated.merged_count} memories")
```

### Memory Expiration

Automatically clean up old memories.

```python
# Configure expiration
store = MemoryStore(
    backend="chromadb",
    expiration_config=ExpirationConfig(
        enabled=True,
        max_age_days={
            MemoryCategory.EPHEMERAL: 1,
            MemoryCategory.WORKING: 7,
            MemoryCategory.EPISODIC: 90
        }
    )
)

# Manual expiration
expired = await store.expire_old_memories(max_age_days=30)
```

## Memory Relationships

### Linking Memories

```python
# Store with relationships
await store.store(MemoryEntry(
    id="detail-001",
    content="Specific implementation detail",
    category=MemoryCategory.SEMANTIC,
    metadata=MemoryMetadata(
        relationships=["overview-001", "task-123"]
    )
))

# Query related memories
related = await store.get_related("overview-001")
```

### Memory Graphs

```python
# Build memory graph
graph = await store.build_graph(
    root_id="project-001",
    max_depth=3
)

# Traverse relationships
for node in graph.traverse():
    print(f"{node.id}: {node.content[:50]}...")
```

## Agent Integration

### Context Retrieval

```python
class MemoryAwareAgent(BaseAgent):
    def __init__(self, provider, memory: MemoryStore):
        super().__init__(provider)
        self.memory = memory

    async def execute(self, task: Task) -> TaskResult:
        # Get relevant context
        context = await self._build_context(task)

        # Include in prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nTask: {task.description}"}
        ]

        response = await self.provider.complete(messages)
        return TaskResult(output=response.content)

    async def _build_context(self, task: Task) -> str:
        memories = await self.memory.search_semantic(
            query=task.description,
            limit=5
        )
        return "\n".join(m.entry.content for m in memories)
```

### Learning from Results

```python
async def learn_from_result(self, task: Task, result: TaskResult):
    """Store successful patterns for future use."""
    if result.success:
        await self.memory.store(MemoryEntry(
            id=f"learning-{task.id}",
            content=f"Task: {task.description}\nApproach: {result.approach}\nOutcome: Success",
            category=MemoryCategory.PROCEDURAL,
            priority=MemoryPriority.HIGH,
            metadata=MemoryMetadata(
                tags=task.tags + ["successful"],
                source="agent_learning"
            )
        ))
```

## Performance Optimization

### Batch Operations

```python
# Batch store
entries = [MemoryEntry(...) for _ in range(100)]
await store.store_batch(entries)

# Batch retrieve
memories = await store.retrieve_batch(["id1", "id2", "id3"])
```

### Caching

```python
store = MemoryStore(
    backend="chromadb",
    cache_config=CacheConfig(
        enabled=True,
        max_size=1000,
        ttl=300  # seconds
    )
)
```

### Index Optimization

```python
# Rebuild indices for faster search
await store.optimize_indices()

# Get storage statistics
stats = await store.get_stats()
print(f"Total memories: {stats.total_count}")
print(f"Index size: {stats.index_size_mb}MB")
```

## Best Practices

1. **Choose appropriate categories** - Match memory type to content
2. **Set priorities wisely** - Protect important memories
3. **Use tags effectively** - Enable filtered retrieval
4. **Regular consolidation** - Prevent memory bloat
5. **Monitor storage** - Track size and performance
6. **Backup regularly** - Prevent data loss

## See Also

- [Memory API Reference](../api/memory-api.md)
- [Storage Configuration](configuration.md)
- [Agent Development](agent-development.md)
