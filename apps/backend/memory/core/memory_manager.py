"""Central memory coordinator for the memory subsystem.

Provides unified API for all memory operations across
episodic, semantic, and H-MEM tiers.

Part of Phase 2: Memory System Architecture
"""

import asyncio
import logging
import threading
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from ..types.episode_types import EpisodeRecord
from ..types.memory_types import MemoryStats, MemoryTier
from ..types.query_types import MemoryQuery, QueryResult

if TYPE_CHECKING:
    from .memory_bridge import MemoryBridge
    from .memory_config import MemorySystemConfig


logger = logging.getLogger(__name__)


# Module-level singleton instance
_memory_manager_instance: Optional["MemoryManager"] = None
_manager_lock = threading.Lock()


def get_memory_manager(
    config: Optional["MemorySystemConfig"] = None,
) -> "MemoryManager":
    """Get or create the singleton MemoryManager instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        The singleton MemoryManager instance
    """
    global _memory_manager_instance

    if _memory_manager_instance is None:
        with _manager_lock:
            if _memory_manager_instance is None:
                _memory_manager_instance = MemoryManager(config)

    return _memory_manager_instance


class MemoryManager:
    """Central coordinator for all memory operations.

    Manages episodic, semantic, and H-MEM tiered memory,
    providing a unified API for storage and retrieval.

    Implements:
    - Episode storage and retrieval
    - Semantic search with embeddings
    - H-MEM tier coordination (L1/L2/L3)
    - Background maintenance tasks
    - Statistics and monitoring

    Usage:
        manager = get_memory_manager(config)

        # Store an episode
        episode_id = await manager.store_episode(episode)

        # Search episodes
        results = await manager.search_episodes(
            MemoryQuery().by_agent("coder").successful_only()
        )

        # Semantic search
        results = await manager.semantic_search(
            "error handling patterns",
            limit=10
        )
    """

    def __init__(self, config: Optional["MemorySystemConfig"] = None):
        """Initialize the memory manager.

        Args:
            config: Memory system configuration
        """
        from .memory_config import load_memory_config

        self._config = config or load_memory_config()
        self._initialized = False
        self._lock = threading.RLock()

        # Tier stores (lazy initialized)
        self._l1_cache: Any | None = None
        self._l2_session: Any | None = None
        self._l3_persistent: Any | None = None

        # Semantic store (lazy initialized)
        self._semantic_store: Any | None = None

        # Bridge for external sync
        self._bridge: MemoryBridge | None = None

        # Statistics
        self._stats = MemoryStats()
        self._access_counts: dict[str, int] = {}

        # Background task handle
        self._maintenance_task: asyncio.Task | None = None

        logger.info("MemoryManager created with config: %s", self._config)

    async def initialize(self) -> None:
        """Initialize all memory stores.

        Should be called before first use. Safe to call multiple times.
        """
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            logger.info("Initializing memory subsystem...")

            # Initialize tier stores
            # Note: Actual implementations in hmem/ module
            # These are placeholder references
            self._l1_cache = {}  # Will be L1Cache instance
            self._l2_session = {}  # Will be L2Session instance
            self._l3_persistent = {}  # Will be L3Persistent instance

            # Initialize semantic store
            self._semantic_store = {}  # Will be SemanticStore instance

            # Start background maintenance
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())

            self._initialized = True
            logger.info("Memory subsystem initialized")

    async def shutdown(self) -> None:
        """Gracefully shutdown memory subsystem."""
        logger.info("Shutting down memory subsystem...")

        # Cancel maintenance task
        if self._maintenance_task:
            self._maintenance_task.cancel()
            try:
                await self._maintenance_task
            except asyncio.CancelledError:
                pass

        # Flush L1 cache to L2
        await self._flush_cache()

        # Close connections
        # L3 persistent store cleanup

        self._initialized = False
        logger.info("Memory subsystem shutdown complete")

    # ===== Episode Operations =====

    async def store_episode(self, episode: EpisodeRecord) -> str:
        """Store an episode record.

        Episodes are stored in L1 cache initially and promoted
        to L2/L3 based on access patterns and policies.

        Args:
            episode: The episode record to store

        Returns:
            The episode ID
        """
        await self._ensure_initialized()

        logger.debug("Storing episode: %s", episode.id)

        # Update timestamp
        episode.updated_at = datetime.utcnow()

        # Store in L1 cache first (hot path)
        self._store_in_tier(episode, MemoryTier.L1_CACHE)

        # Also persist to L3 for durability
        await self._persist_episode(episode)

        # Update stats
        self._stats.total_records += 1

        logger.info("Episode stored: %s (agent=%s)", episode.id, episode.agent_id)
        return episode.id

    async def get_episode(self, episode_id: str) -> EpisodeRecord | None:
        """Retrieve an episode by ID.

        Checks tiers in order: L1 -> L2 -> L3
        Promotes frequently accessed episodes to faster tiers.

        Args:
            episode_id: The episode ID to retrieve

        Returns:
            The episode record or None if not found
        """
        await self._ensure_initialized()

        # Check L1 cache first
        if episode := self._get_from_tier(episode_id, MemoryTier.L1_CACHE):
            self._record_access(episode_id)
            return episode

        # Check L2 session
        if episode := self._get_from_tier(episode_id, MemoryTier.L2_SESSION):
            self._record_access(episode_id)
            # Promote to L1 if frequently accessed
            if self._should_promote(episode_id):
                self._promote(episode, MemoryTier.L1_CACHE)
            return episode

        # Check L3 persistent
        if episode := await self._get_from_persistent(episode_id):
            self._record_access(episode_id)
            # Promote to L2
            if self._should_promote(episode_id):
                self._promote(episode, MemoryTier.L2_SESSION)
            return episode

        return None

    async def search_episodes(self, query: MemoryQuery) -> QueryResult[EpisodeRecord]:
        """Search episodes matching query criteria.

        Args:
            query: The search query specification

        Returns:
            QueryResult containing matching episodes
        """
        await self._ensure_initialized()

        start_time = datetime.utcnow()

        # Execute query against persistent store
        episodes = await self._execute_query(query)

        # Apply semantic search if specified
        if query.semantic_query:
            episodes = await self._apply_semantic_filter(
                episodes, query.semantic_query, query.similarity_threshold
            )

        # Build result
        query_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return QueryResult(
            items=episodes[: query.pagination.limit],
            total_count=len(episodes),
            query_time_ms=query_time,
            pagination=query.pagination,
        )

    # ===== Semantic Operations =====

    async def store_embedding(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        episode_id: str | None = None,
    ) -> str:
        """Store text with embedding for semantic search.

        Args:
            text: Text to embed and store
            metadata: Optional metadata to associate
            episode_id: Optional link to episode

        Returns:
            The embedding record ID
        """
        await self._ensure_initialized()

        # Generate embedding (placeholder - actual impl in embeddings module)
        embedding = await self._generate_embedding(text)

        # Store in semantic store
        record_id = await self._store_semantic(
            text=text,
            embedding=embedding,
            metadata=metadata or {},
            episode_id=episode_id,
        )

        return record_id

    async def semantic_search(
        self, query: str, limit: int = 10, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Search semantically similar content.

        Args:
            query: Search query text
            limit: Maximum results to return
            filters: Optional metadata filters

        Returns:
            List of matching records with similarity scores
        """
        await self._ensure_initialized()

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Search semantic store
        results = await self._search_semantic(
            embedding=query_embedding, limit=limit, filters=filters
        )

        return results

    # ===== Context Building =====

    async def get_context(self, task_id: str, max_tokens: int = 4000) -> dict[str, Any]:
        """Build context for a task from memory.

        Combines relevant episodes, semantic search results,
        and working memory into a context dictionary.

        Args:
            task_id: The task to build context for
            max_tokens: Maximum context tokens

        Returns:
            Context dictionary with relevant memories
        """
        await self._ensure_initialized()

        context = {
            "task_id": task_id,
            "episodes": [],
            "semantic_results": [],
            "working_memory": {},
        }

        # Get recent episodes for this task
        query = MemoryQuery().by_task(task_id).limit(10)
        episode_results = await self.search_episodes(query)
        context["episodes"] = [e.to_dict() for e in episode_results.items]

        return context

    # ===== Statistics =====

    def get_stats(self) -> MemoryStats:
        """Get memory subsystem statistics."""
        return self._stats

    # ===== Private Methods =====

    async def _ensure_initialized(self) -> None:
        """Ensure manager is initialized."""
        if not self._initialized:
            await self.initialize()

    def _store_in_tier(self, episode: EpisodeRecord, tier: MemoryTier) -> None:
        """Store episode in specified tier."""
        tier_store = self._get_tier_store(tier)
        if tier_store is not None:
            tier_store[episode.id] = episode

    def _get_from_tier(
        self, episode_id: str, tier: MemoryTier
    ) -> EpisodeRecord | None:
        """Get episode from specified tier."""
        tier_store = self._get_tier_store(tier)
        if tier_store:
            return tier_store.get(episode_id)
        return None

    def _get_tier_store(self, tier: MemoryTier) -> dict | None:
        """Get the store for a tier."""
        stores = {
            MemoryTier.L1_CACHE: self._l1_cache,
            MemoryTier.L2_SESSION: self._l2_session,
            MemoryTier.L3_PERSISTENT: self._l3_persistent,
        }
        return stores.get(tier)

    async def _persist_episode(self, episode: EpisodeRecord) -> None:
        """Persist episode to L3."""
        # Placeholder - actual implementation in episodic module
        if self._l3_persistent is not None:
            self._l3_persistent[episode.id] = episode

    async def _get_from_persistent(self, episode_id: str) -> EpisodeRecord | None:
        """Get episode from L3 persistent store."""
        if self._l3_persistent:
            return self._l3_persistent.get(episode_id)
        return None

    def _record_access(self, episode_id: str) -> None:
        """Record an access for promotion decisions."""
        self._access_counts[episode_id] = self._access_counts.get(episode_id, 0) + 1

    def _should_promote(self, episode_id: str) -> bool:
        """Check if episode should be promoted to faster tier."""
        threshold = self._config.l1.promote_access_threshold
        return self._access_counts.get(episode_id, 0) >= threshold

    def _promote(self, episode: EpisodeRecord, target_tier: MemoryTier) -> None:
        """Promote episode to target tier."""
        self._store_in_tier(episode, target_tier)
        logger.debug("Promoted episode %s to %s", episode.id, target_tier)

    async def _execute_query(self, query: MemoryQuery) -> list[EpisodeRecord]:
        """Execute query against storage."""
        # Placeholder - actual implementation uses SQLite FTS
        results = []

        # Search L3 persistent store
        if self._l3_persistent:
            for episode in self._l3_persistent.values():
                if self._matches_query(episode, query):
                    results.append(episode)

        return results

    def _matches_query(self, episode: EpisodeRecord, query: MemoryQuery) -> bool:
        """Check if episode matches query criteria."""
        if query.agent_id and episode.agent_id != query.agent_id:
            return False
        if query.agent_type and episode.agent_type != query.agent_type:
            return False
        if query.task_id and episode.task_id != query.task_id:
            return False
        if query.outcome and episode.outcome != query.outcome:
            return False
        if query.since and episode.created_at < query.since:
            return False
        if query.until and episode.created_at > query.until:
            return False
        return True

    async def _apply_semantic_filter(
        self, episodes: list[EpisodeRecord], query: str, threshold: float
    ) -> list[EpisodeRecord]:
        """Filter episodes by semantic similarity."""
        # Placeholder - actual implementation uses embeddings
        return episodes

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text."""
        # Placeholder - actual implementation uses embedder
        return [0.0] * self._config.embedding_dimension

    async def _store_semantic(
        self,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
        episode_id: str | None,
    ) -> str:
        """Store in semantic store."""
        import uuid

        record_id = str(uuid.uuid4())
        # Placeholder - actual implementation in semantic module
        return record_id

    async def _search_semantic(
        self, embedding: list[float], limit: int, filters: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        """Search semantic store."""
        # Placeholder - actual implementation in semantic module
        return []

    async def _flush_cache(self) -> None:
        """Flush L1 cache to L2."""
        if self._l1_cache and self._l2_session:
            for episode_id, episode in self._l1_cache.items():
                self._l2_session[episode_id] = episode
            self._l1_cache.clear()

    async def _maintenance_loop(self) -> None:
        """Background maintenance task."""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                await self._run_maintenance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Maintenance error: %s", e)

    async def _run_maintenance(self) -> None:
        """Run maintenance tasks."""
        # Evict stale L1 cache entries
        # Compact L3 storage
        # Update statistics
        logger.debug("Running memory maintenance")
