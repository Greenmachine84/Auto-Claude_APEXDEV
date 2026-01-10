"""
Result Handler - Phase 8 Implementation.

Tool result processing and normalization.

World-Class Standards:
- Result normalization
- Format conversion
- Streaming support
- Error enrichment
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..models import ToolResult

logger = logging.getLogger(__name__)


@dataclass
class StreamChunk:
    """Streaming result chunk."""

    content: str
    index: int
    is_final: bool
    metadata: dict[str, Any]


class ResultHandler:
    """
    Tool result processing.

    Features:
    - Result normalization
    - Format conversion
    - Streaming support
    - Error enrichment
    """

    def __init__(
        self,
        max_output_size: int = 10 * 1024 * 1024,  # 10MB
        truncate_output: bool = True,
    ) -> None:
        """Initialize handler."""
        self.max_output_size = max_output_size
        self.truncate_output = truncate_output

        logger.info("ResultHandler initialized")

    def normalize(
        self,
        output: Any,
        tool_name: str,
    ) -> ToolResult:
        """
        Normalize tool output to ToolResult.

        Args:
            output: Raw tool output
            tool_name: Name of tool that produced output

        Returns:
            Normalized ToolResult
        """
        timestamp = datetime.utcnow().isoformat()

        # Already a ToolResult
        if isinstance(output, ToolResult):
            output.metadata["normalized_at"] = timestamp
            return output

        # Dict with error field
        if isinstance(output, dict):
            if "error" in output and output["error"]:
                return ToolResult(
                    output=output.get("output"),
                    error=str(output["error"]),
                    metadata={
                        "tool_name": tool_name,
                        "normalized_at": timestamp,
                        **output.get("metadata", {}),
                    },
                )

            return ToolResult(
                output=output,
                error=None,
                metadata={
                    "tool_name": tool_name,
                    "normalized_at": timestamp,
                },
            )

        # Exception
        if isinstance(output, Exception):
            return ToolResult(
                output=None,
                error=str(output),
                metadata={
                    "tool_name": tool_name,
                    "normalized_at": timestamp,
                    "exception_type": type(output).__name__,
                },
            )

        # None
        if output is None:
            return ToolResult(
                output=None,
                error=None,
                metadata={
                    "tool_name": tool_name,
                    "normalized_at": timestamp,
                    "empty_result": True,
                },
            )

        # Apply size limits
        output = self._apply_size_limits(output)

        # Default: wrap as output
        return ToolResult(
            output=output,
            error=None,
            metadata={
                "tool_name": tool_name,
                "normalized_at": timestamp,
            },
        )

    def to_json(self, result: ToolResult) -> str:
        """Convert result to JSON string."""
        return json.dumps(
            {
                "output": self._serialize(result.output),
                "error": result.error,
                "metadata": result.metadata,
                "success": result.success,
            },
            indent=2,
        )

    def to_dict(self, result: ToolResult) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "output": self._serialize(result.output),
            "error": result.error,
            "metadata": result.metadata,
            "success": result.success,
        }

    def to_markdown(self, result: ToolResult) -> str:
        """Convert result to Markdown."""
        lines = []

        if result.success:
            lines.append("## Result")
            lines.append("")

            if isinstance(result.output, dict):
                lines.append("```json")
                lines.append(json.dumps(result.output, indent=2))
                lines.append("```")
            elif isinstance(result.output, str):
                lines.append(result.output)
            else:
                lines.append(f"```\n{result.output}\n```")
        else:
            lines.append("## Error")
            lines.append("")
            lines.append(f"**Error:** {result.error}")

        if result.metadata:
            lines.append("")
            lines.append("### Metadata")
            lines.append("")
            for key, value in result.metadata.items():
                lines.append(f"- **{key}:** {value}")

        return "\n".join(lines)

    def to_openai_message(self, result: ToolResult) -> dict[str, Any]:
        """Convert result to OpenAI tool message format."""
        return {
            "role": "tool",
            "content": json.dumps(self._serialize(result.output))
            if result.success
            else result.error,
            "tool_call_id": result.metadata.get("tool_call_id", ""),
        }

    def to_anthropic_result(self, result: ToolResult) -> dict[str, Any]:
        """Convert result to Anthropic tool result format."""
        return {
            "type": "tool_result",
            "tool_use_id": result.metadata.get("tool_use_id", ""),
            "content": self._serialize(result.output)
            if result.success
            else result.error,
            "is_error": not result.success,
        }

    def enrich_error(
        self,
        result: ToolResult,
        context: dict[str, Any],
    ) -> ToolResult:
        """
        Enrich error with additional context.

        Args:
            result: Result with error
            context: Additional context

        Returns:
            Enriched result
        """
        if result.success:
            return result

        result.metadata.update(
            {
                "error_context": context,
                "enriched_at": datetime.utcnow().isoformat(),
            }
        )

        # Add suggestions if possible
        suggestions = self._get_error_suggestions(result.error)
        if suggestions:
            result.metadata["suggestions"] = suggestions

        return result

    def merge_results(
        self,
        results: list[ToolResult],
    ) -> ToolResult:
        """
        Merge multiple results into one.

        Args:
            results: List of results to merge

        Returns:
            Merged result
        """
        if not results:
            return ToolResult(
                output=[],
                error=None,
                metadata={"merged": True, "count": 0},
            )

        outputs = []
        errors = []
        all_metadata = {}

        for i, result in enumerate(results):
            if result.output is not None:
                outputs.append(result.output)
            if result.error:
                errors.append({"index": i, "error": result.error})
            all_metadata[f"result_{i}"] = result.metadata

        return ToolResult(
            output=outputs,
            error=errors[0]["error"]
            if len(errors) == 1
            else (f"{len(errors)} errors occurred" if errors else None),
            metadata={
                "merged": True,
                "count": len(results),
                "success_count": len(results) - len(errors),
                "error_count": len(errors),
                "errors": errors if errors else None,
                "merged_at": datetime.utcnow().isoformat(),
            },
        )

    async def stream_result(
        self,
        result: ToolResult,
        chunk_size: int = 1024,
    ):
        """
        Stream a large result in chunks.

        Args:
            result: Result to stream
            chunk_size: Size of each chunk

        Yields:
            StreamChunk objects
        """
        if result.error:
            yield StreamChunk(
                content=result.error,
                index=0,
                is_final=True,
                metadata={"type": "error"},
            )
            return

        content = self._serialize_string(result.output)
        total_chunks = (len(content) + chunk_size - 1) // chunk_size

        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(content))

            yield StreamChunk(
                content=content[start:end],
                index=i,
                is_final=(i == total_chunks - 1),
                metadata={
                    "total_chunks": total_chunks,
                    "progress": (i + 1) / total_chunks,
                },
            )

    def _apply_size_limits(self, output: Any) -> Any:
        """Apply size limits to output."""
        if isinstance(output, str):
            if len(output) > self.max_output_size:
                if self.truncate_output:
                    return output[: self.max_output_size] + "\n... [truncated]"
                raise ValueError(f"Output exceeds max size: {len(output)}")

        elif isinstance(output, bytes):
            if len(output) > self.max_output_size:
                if self.truncate_output:
                    return output[: self.max_output_size]
                raise ValueError(f"Output exceeds max size: {len(output)}")

        return output

    def _serialize(self, obj: Any) -> Any:
        """Serialize object for JSON."""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        if isinstance(obj, (list, tuple)):
            return [self._serialize(item) for item in obj]
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        if hasattr(obj, "__dict__"):
            return self._serialize(obj.__dict__)
        return str(obj)

    def _serialize_string(self, obj: Any) -> str:
        """Serialize object to string."""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        return json.dumps(self._serialize(obj))

    def _get_error_suggestions(self, error: str | None) -> list[str]:
        """Get suggestions for common errors."""
        if not error:
            return []

        suggestions = []
        error_lower = error.lower()

        if "permission denied" in error_lower:
            suggestions.append("Check file permissions")
            suggestions.append("Run with elevated privileges if needed")

        if "not found" in error_lower:
            suggestions.append("Verify the path or resource exists")
            suggestions.append("Check for typos in the name")

        if "timeout" in error_lower:
            suggestions.append("Increase timeout value")
            suggestions.append("Check network connectivity")

        if "connection" in error_lower:
            suggestions.append("Check network connectivity")
            suggestions.append("Verify the service is running")

        return suggestions
