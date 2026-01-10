"""Stream buffer for partial response accumulation.

Part of Phase 2: LLM Architecture
"""

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from ..types import FinishReason, StreamChunk, ToolCall

logger = logging.getLogger(__name__)


@dataclass
class BufferSnapshot:
    """Snapshot of buffer state at a point in time."""

    content: str
    chunk_count: int
    tool_calls: list[ToolCall]
    is_complete: bool
    finish_reason: FinishReason | None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class StreamBuffer:
    """Buffer for accumulating streaming response chunks.

    Features:
    - Thread-safe accumulation
    - Snapshot capability
    - Callback on chunk arrival
    - Tool call detection
    """

    def __init__(
        self,
        on_chunk: Callable[[str], None] | None = None,
        on_complete: Callable[[str], None] | None = None,
        on_tool_call: Callable[[ToolCall], None] | None = None,
    ):
        self._content = ""
        self._chunks: list[StreamChunk] = []
        self._tool_calls: dict[str, ToolCall] = {}  # id -> ToolCall
        self._tool_call_buffers: dict[str, str] = {}  # id -> partial args
        self._finish_reason: FinishReason | None = None
        self._is_complete = False
        self._lock = threading.Lock()

        self._on_chunk = on_chunk
        self._on_complete = on_complete
        self._on_tool_call = on_tool_call

    def append(self, chunk: StreamChunk) -> None:
        """Append a chunk to the buffer."""
        with self._lock:
            self._chunks.append(chunk)

            # Accumulate content
            if chunk.delta:
                self._content += chunk.delta
                if self._on_chunk:
                    self._on_chunk(chunk.delta)

            # Process tool calls
            for tc in chunk.tool_calls:
                self._process_tool_call(tc)

            # Check for completion
            if chunk.is_final or chunk.finish_reason:
                self._finish_reason = chunk.finish_reason
                self._is_complete = True
                if self._on_complete:
                    self._on_complete(self._content)

    def _process_tool_call(self, tc: ToolCall) -> None:
        """Process a tool call from a chunk."""
        if tc.id not in self._tool_calls:
            # New tool call
            self._tool_calls[tc.id] = ToolCall(id=tc.id, name=tc.name, arguments={})
            self._tool_call_buffers[tc.id] = ""

        # Accumulate arguments if streaming as string
        if tc.arguments:
            if isinstance(tc.arguments, str):
                self._tool_call_buffers[tc.id] += tc.arguments
            else:
                self._tool_calls[tc.id].arguments = tc.arguments
                if self._on_tool_call:
                    self._on_tool_call(self._tool_calls[tc.id])

    def finalize_tool_calls(self) -> list[ToolCall]:
        """Finalize tool calls by parsing accumulated argument strings."""
        import json

        for tc_id, args_str in self._tool_call_buffers.items():
            if args_str and tc_id in self._tool_calls:
                try:
                    self._tool_calls[tc_id].arguments = json.loads(args_str)
                    if self._on_tool_call:
                        self._on_tool_call(self._tool_calls[tc_id])
                except json.JSONDecodeError:
                    logger.warning("Failed to parse tool call args: %s", args_str[:100])

        return list(self._tool_calls.values())

    def snapshot(self) -> BufferSnapshot:
        """Get current buffer snapshot."""
        with self._lock:
            return BufferSnapshot(
                content=self._content,
                chunk_count=len(self._chunks),
                tool_calls=list(self._tool_calls.values()),
                is_complete=self._is_complete,
                finish_reason=self._finish_reason,
            )

    @property
    def content(self) -> str:
        """Get accumulated content."""
        with self._lock:
            return self._content

    @property
    def is_complete(self) -> bool:
        """Check if stream is complete."""
        return self._is_complete

    @property
    def chunk_count(self) -> int:
        """Get number of chunks received."""
        return len(self._chunks)

    @property
    def tool_calls(self) -> list[ToolCall]:
        """Get tool calls (may be incomplete if streaming)."""
        return list(self._tool_calls.values())

    def clear(self) -> None:
        """Clear buffer state."""
        with self._lock:
            self._content = ""
            self._chunks.clear()
            self._tool_calls.clear()
            self._tool_call_buffers.clear()
            self._finish_reason = None
            self._is_complete = False
