"""LLM Streaming module.

Provides streaming infrastructure:
- Stream handler for async iteration
- SSE adapter for Server-Sent Events
- Chunk processor for delta accumulation

Part of Phase 2: LLM Architecture
"""

from .stream_handler import StreamHandler, StreamState
from .sse_adapter import SSEAdapter, SSEEvent
from .chunk_processor import ChunkProcessor, ProcessedChunk

__all__ = [
    "StreamHandler",
    "StreamState",
    "SSEAdapter",
    "SSEEvent",
    "ChunkProcessor",
    "ProcessedChunk",
]
