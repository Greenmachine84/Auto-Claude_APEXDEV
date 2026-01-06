"""Chunk processor for stream delta accumulation.

Part of Phase 2: LLM Architecture
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..types import StreamChunk, ToolCall, FinishReason

logger = logging.getLogger(__name__)


@dataclass
class ProcessedChunk:
    """A processed chunk with accumulated state."""
    index: int
    delta: str
    accumulated: str
    tool_calls: List[ToolCall]
    finish_reason: Optional[FinishReason]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChunkProcessor:
    """Processes and accumulates stream chunks."""
    
    def __init__(self):
        self._accumulated = ""
        self._tool_calls: Dict[str, ToolCall] = {}  # id -> ToolCall
        self._tool_call_args: Dict[str, str] = {}  # id -> accumulated args
        self._chunk_count = 0
        self._finish_reason: Optional[FinishReason] = None
    
    def process(self, chunk: StreamChunk) -> ProcessedChunk:
        """Process a chunk and return accumulated state."""
        self._chunk_count += 1
        
        # Accumulate content
        if chunk.delta:
            self._accumulated += chunk.delta
        
        # Process tool calls
        for tc in chunk.tool_calls:
            if tc.id not in self._tool_calls:
                self._tool_calls[tc.id] = ToolCall(
                    id=tc.id, name=tc.name, arguments={}
                )
                self._tool_call_args[tc.id] = ""
            
            # Accumulate arguments (might come in chunks)
            if tc.arguments:
                if isinstance(tc.arguments, str):
                    self._tool_call_args[tc.id] += tc.arguments
                else:
                    self._tool_calls[tc.id].arguments = tc.arguments
        
        # Parse accumulated tool call arguments
        for tc_id, args_str in self._tool_call_args.items():
            if args_str:
                try:
                    self._tool_calls[tc_id].arguments = json.loads(args_str)
                except json.JSONDecodeError:
                    pass  # Still accumulating
        
        # Track finish reason
        if chunk.finish_reason:
            self._finish_reason = chunk.finish_reason
        
        return ProcessedChunk(
            index=self._chunk_count,
            delta=chunk.delta,
            accumulated=self._accumulated,
            tool_calls=list(self._tool_calls.values()),
            finish_reason=self._finish_reason
        )
    
    def reset(self) -> None:
        """Reset processor state."""
        self._accumulated = ""
        self._tool_calls.clear()
        self._tool_call_args.clear()
        self._chunk_count = 0
        self._finish_reason = None
    
    @property
    def content(self) -> str:
        """Get accumulated content."""
        return self._accumulated
    
    @property
    def tool_calls(self) -> List[ToolCall]:
        """Get processed tool calls."""
        return list(self._tool_calls.values())
    
    @property
    def is_complete(self) -> bool:
        """Check if stream is complete."""
        return self._finish_reason is not None
    
    @property
    def chunk_count(self) -> int:
        """Get number of processed chunks."""
        return self._chunk_count
