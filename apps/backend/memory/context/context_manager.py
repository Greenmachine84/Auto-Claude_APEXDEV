"""Central context manager for agent sessions.

Part of Phase 2: Memory System Architecture
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from .context_compressor import CompressionResult, ContextCompressor
from .context_window import ContextEntry, ContextPriority, ContextRole, ContextWindow

logger = logging.getLogger(__name__)


@dataclass
class ContextStats:
    """Statistics for context management."""

    total_messages: int = 0
    total_tokens: int = 0
    compressions: int = 0
    evictions: int = 0


class ContextManager:
    """Manages context for an agent session."""

    def __init__(
        self,
        max_tokens: int = 8000,
        reserve_tokens: int = 1000,
        auto_compress: bool = True,
        compress_threshold: float = 0.8,
        summarize_fn: Callable[[str], str] | None = None,
    ):
        self._window = ContextWindow(
            max_tokens=max_tokens, reserve_tokens=reserve_tokens
        )
        self._compressor = ContextCompressor(summarize_fn=summarize_fn)
        self._auto_compress = auto_compress
        self._compress_threshold = compress_threshold
        self._stats = ContextStats()
        self._session_id = str(uuid.uuid4())

    def add_system(self, content: str, token_count: int = 0) -> str:
        return self._add_entry(
            ContextRole.SYSTEM,
            content,
            token_count,
            ContextPriority.CRITICAL,
            pinned=True,
        )

    def add_user(self, content: str, token_count: int = 0) -> str:
        return self._add_entry(
            ContextRole.USER, content, token_count, ContextPriority.HIGH
        )

    def add_assistant(self, content: str, token_count: int = 0) -> str:
        return self._add_entry(
            ContextRole.ASSISTANT, content, token_count, ContextPriority.NORMAL
        )

    def add_tool(self, content: str, token_count: int = 0) -> str:
        return self._add_entry(
            ContextRole.TOOL, content, token_count, ContextPriority.NORMAL
        )

    def _add_entry(
        self,
        role: ContextRole,
        content: str,
        token_count: int,
        priority: ContextPriority,
        pinned: bool = False,
    ) -> str:
        entry_id = str(uuid.uuid4())
        tokens = token_count or len(content.split()) * 2  # Rough estimate

        entry = ContextEntry(
            id=entry_id,
            role=role,
            content=content,
            priority=priority,
            token_count=tokens,
            pinned=pinned,
        )

        if self._auto_compress and self._should_compress():
            self._compress()

        self._window.add(entry)
        self._stats.total_messages += 1
        self._stats.total_tokens = self._window.total_tokens()

        return entry_id

    def get_messages(self) -> list[dict[str, str]]:
        return self._window.get_messages()

    def get_entries(self) -> list[ContextEntry]:
        return self._window.get_entries()

    def clear(self) -> int:
        count = self._window.clear()
        self._stats = ContextStats()
        return count

    def pin(self, entry_id: str) -> bool:
        return self._window.pin(entry_id)

    def unpin(self, entry_id: str) -> bool:
        return self._window.unpin(entry_id)

    def compress(self) -> CompressionResult:
        return self._compress()

    def _should_compress(self) -> bool:
        usage = self._window.total_tokens() / (
            self._window.total_tokens() + self._window.available_tokens()
        )
        return usage > self._compress_threshold

    def _compress(self) -> CompressionResult:
        entries = self._window.get_entries()
        target = int(self._window.total_tokens() * 0.6)

        compressed, result = self._compressor.compress(entries, target)

        if result.entries_merged > 0:
            self._window.clear()
            for entry in compressed:
                self._window.add(entry)
            self._stats.compressions += 1

        return result

    def available_tokens(self) -> int:
        return self._window.available_tokens()

    def stats(self) -> ContextStats:
        return self._stats

    @property
    def session_id(self) -> str:
        return self._session_id
