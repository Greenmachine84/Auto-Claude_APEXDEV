"""Memory core module - Central memory subsystem coordination.

Provides the core infrastructure for memory operations including:
- MemoryManager: Central coordinator for all memory tiers
- MemoryConfig: Configuration management
- MemoryBridge: Cross-system synchronization

Part of Phase 2: Memory System Architecture
See: docs/architecture/PHASE2_MEMORY_LLM_ARCHITECTURE.md
"""

from .memory_manager import MemoryManager, get_memory_manager
from .memory_config import (
    MemorySystemConfig,
    L1CacheConfig,
    L2SessionConfig,
    L3PersistentConfig,
    load_memory_config,
)
from .memory_bridge import MemoryBridge, SyncResult, SyncStatus

__all__ = [
    # Manager
    "MemoryManager",
    "get_memory_manager",
    # Config
    "MemorySystemConfig",
    "L1CacheConfig",
    "L2SessionConfig",
    "L3PersistentConfig",
    "load_memory_config",
    # Bridge
    "MemoryBridge",
    "SyncResult",
    "SyncStatus",
]
