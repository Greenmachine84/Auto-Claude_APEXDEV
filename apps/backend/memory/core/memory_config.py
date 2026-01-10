"""Memory system configuration management.

Provides configuration classes and loading utilities
for the memory subsystem.

Part of Phase 2: Memory System Architecture
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class L1CacheConfig:
    """Configuration for L1 in-memory cache."""

    max_items: int = 1000
    max_size_mb: int = 100
    ttl_seconds: int = 3600  # 1 hour
    eviction_policy: str = "lru"  # lru, lfu, fifo
    promote_access_threshold: int = 5

    def validate(self) -> None:
        """Validate configuration values."""
        if self.max_items <= 0:
            raise ValueError("max_items must be positive")
        if self.max_size_mb <= 0:
            raise ValueError("max_size_mb must be positive")
        if self.eviction_policy not in ("lru", "lfu", "fifo"):
            raise ValueError(f"Invalid eviction_policy: {self.eviction_policy}")


@dataclass
class L2SessionConfig:
    """Configuration for L2 session-scoped memory."""

    max_items: int = 10000
    max_size_mb: int = 1024
    session_ttl_hours: int = 24
    persist_on_shutdown: bool = True

    def validate(self) -> None:
        """Validate configuration values."""
        if self.max_items <= 0:
            raise ValueError("max_items must be positive")
        if self.max_size_mb <= 0:
            raise ValueError("max_size_mb must be positive")


@dataclass
class L3PersistentConfig:
    """Configuration for L3 persistent storage."""

    db_path: str = "memory.db"
    enable_fts: bool = True  # Full-text search
    enable_wal: bool = True  # Write-ahead logging
    vacuum_interval_hours: int = 24
    max_connections: int = 5
    busy_timeout_ms: int = 5000

    def validate(self) -> None:
        """Validate configuration values."""
        if not self.db_path:
            raise ValueError("db_path is required")


@dataclass
class RetentionConfig:
    """Configuration for memory retention policies."""

    max_episodes_per_agent: int = 1000
    retention_days: int = 90
    preserve_critical: bool = True  # Never delete critical episodes
    compress_after_days: int = 30
    delete_ephemeral_hours: int = 24

    def validate(self) -> None:
        """Validate configuration values."""
        if self.max_episodes_per_agent <= 0:
            raise ValueError("max_episodes_per_agent must be positive")
        if self.retention_days <= 0:
            raise ValueError("retention_days must be positive")


@dataclass
class EmbeddingConfig:
    """Configuration for embeddings."""

    dimension: int = 1536
    default_provider: str = "openai"  # One of 8 canonical providers
    default_model: str = "text-embedding-3-small"
    batch_size: int = 100
    normalize: bool = True

    def validate(self) -> None:
        """Validate configuration values."""
        valid_providers = {
            "openai",
            "ollama",
            "voyage",
            "gemini",
            "azure",
            "openrouter",
            "copilot",
            "lmstudio",
        }
        if self.default_provider not in valid_providers:
            raise ValueError(f"Invalid provider: {self.default_provider}")
        if self.dimension <= 0:
            raise ValueError("dimension must be positive")


@dataclass
class SemanticConfig:
    """Configuration for semantic search."""

    similarity_metric: str = "cosine"  # cosine, euclidean, dot
    default_threshold: float = 0.7
    max_results: int = 100
    rerank_enabled: bool = False

    def validate(self) -> None:
        """Validate configuration values."""
        valid_metrics = {"cosine", "euclidean", "dot"}
        if self.similarity_metric not in valid_metrics:
            raise ValueError(f"Invalid similarity_metric: {self.similarity_metric}")
        if not 0.0 <= self.default_threshold <= 1.0:
            raise ValueError("default_threshold must be between 0 and 1")


@dataclass
class MemorySystemConfig:
    """Complete configuration for memory subsystem.

    Aggregates all component configurations with validation.
    """

    # Tier configurations
    l1: L1CacheConfig = field(default_factory=L1CacheConfig)
    l2: L2SessionConfig = field(default_factory=L2SessionConfig)
    l3: L3PersistentConfig = field(default_factory=L3PersistentConfig)

    # Feature configurations
    retention: RetentionConfig = field(default_factory=RetentionConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    semantic: SemanticConfig = field(default_factory=SemanticConfig)

    # Global settings
    data_dir: str = ".autoclaude/memory"
    enable_sync: bool = True
    sync_interval_seconds: int = 60
    debug_mode: bool = False

    # Convenience properties
    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding.dimension

    @property
    def db_path(self) -> str:
        """Get full database path."""
        return str(Path(self.data_dir) / self.l3.db_path)

    def validate(self) -> None:
        """Validate all configurations."""
        self.l1.validate()
        self.l2.validate()
        self.l3.validate()
        self.retention.validate()
        self.embedding.validate()
        self.semantic.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "l1": {
                "max_items": self.l1.max_items,
                "max_size_mb": self.l1.max_size_mb,
                "ttl_seconds": self.l1.ttl_seconds,
                "eviction_policy": self.l1.eviction_policy,
            },
            "l2": {
                "max_items": self.l2.max_items,
                "max_size_mb": self.l2.max_size_mb,
                "session_ttl_hours": self.l2.session_ttl_hours,
            },
            "l3": {
                "db_path": self.l3.db_path,
                "enable_fts": self.l3.enable_fts,
                "enable_wal": self.l3.enable_wal,
            },
            "retention": {
                "max_episodes_per_agent": self.retention.max_episodes_per_agent,
                "retention_days": self.retention.retention_days,
            },
            "embedding": {
                "dimension": self.embedding.dimension,
                "default_provider": self.embedding.default_provider,
                "default_model": self.embedding.default_model,
            },
            "semantic": {
                "similarity_metric": self.semantic.similarity_metric,
                "default_threshold": self.semantic.default_threshold,
            },
            "data_dir": self.data_dir,
            "enable_sync": self.enable_sync,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemorySystemConfig":
        """Create from dictionary."""
        config = cls()

        if "l1" in data:
            config.l1 = L1CacheConfig(**data["l1"])
        if "l2" in data:
            config.l2 = L2SessionConfig(**data["l2"])
        if "l3" in data:
            config.l3 = L3PersistentConfig(**data["l3"])
        if "retention" in data:
            config.retention = RetentionConfig(**data["retention"])
        if "embedding" in data:
            config.embedding = EmbeddingConfig(**data["embedding"])
        if "semantic" in data:
            config.semantic = SemanticConfig(**data["semantic"])

        if "data_dir" in data:
            config.data_dir = data["data_dir"]
        if "enable_sync" in data:
            config.enable_sync = data["enable_sync"]
        if "debug_mode" in data:
            config.debug_mode = data["debug_mode"]

        return config


def load_memory_config(
    config_path: str | None = None, env_prefix: str = "AUTOCLAUDE_MEMORY_"
) -> MemorySystemConfig:
    """Load memory configuration from file and environment.

    Priority (highest to lowest):
    1. Environment variables (AUTOCLAUDE_MEMORY_*)
    2. Config file (memory_config.json)
    3. Default values

    Args:
        config_path: Optional path to config file
        env_prefix: Environment variable prefix

    Returns:
        Loaded and validated configuration
    """
    config = MemorySystemConfig()

    # Try to load from file
    if config_path:
        file_path = Path(config_path)
    else:
        # Look for config in standard locations
        search_paths = [
            Path("memory_config.json"),
            Path(".autoclaude/memory_config.json"),
            Path.home() / ".autoclaude" / "memory_config.json",
        ]
        file_path = None
        for path in search_paths:
            if path.exists():
                file_path = path
                break

    if file_path and file_path.exists():
        try:
            with open(file_path) as f:
                file_config = json.load(f)
            config = MemorySystemConfig.from_dict(file_config)
            logger.info("Loaded memory config from %s", file_path)
        except Exception as e:
            logger.warning("Failed to load config from %s: %s", file_path, e)

    # Override with environment variables
    env_overrides = {
        f"{env_prefix}DATA_DIR": "data_dir",
        f"{env_prefix}L1_MAX_ITEMS": ("l1", "max_items"),
        f"{env_prefix}L1_MAX_SIZE_MB": ("l1", "max_size_mb"),
        f"{env_prefix}L1_TTL_SECONDS": ("l1", "ttl_seconds"),
        f"{env_prefix}L3_DB_PATH": ("l3", "db_path"),
        f"{env_prefix}EMBEDDING_DIMENSION": ("embedding", "dimension"),
        f"{env_prefix}EMBEDDING_PROVIDER": ("embedding", "default_provider"),
        f"{env_prefix}RETENTION_DAYS": ("retention", "retention_days"),
    }

    for env_var, config_path_key in env_overrides.items():
        value = os.environ.get(env_var)
        if value:
            try:
                if isinstance(config_path_key, tuple):
                    section, key = config_path_key
                    section_obj = getattr(config, section)
                    # Convert to appropriate type
                    current_value = getattr(section_obj, key)
                    if isinstance(current_value, int):
                        value = int(value)
                    elif isinstance(current_value, bool):
                        value = value.lower() in ("true", "1", "yes")
                    setattr(section_obj, key, value)
                else:
                    setattr(config, config_path_key, value)
                logger.debug("Applied env override: %s", env_var)
            except Exception as e:
                logger.warning("Failed to apply env var %s: %s", env_var, e)

    # Validate
    config.validate()

    return config
