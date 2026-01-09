"""Semantic search tool.

Semantic code search using embeddings.

Capabilities:
- Natural language queries
- Similarity search
- Code understanding
- Context retrieval
"""

import os

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)


class SemanticSearchTool(BaseTool):
    """Semantic code search.

    Uses embeddings for natural language code search.

    Example:
        tool = SemanticSearchTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "query": "function that handles user authentication",
                "path": "/path/to/repo",
            }
        ))
    """

    name = "semantic_search"
    description = "Semantic code search using embeddings"
    category = ToolCategory.SEARCH
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Natural language search query",
                required=True,
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Directory to search in",
                required=True,
            ),
            ToolParameter(
                name="language",
                type="string",
                description="Filter by language",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="top_k",
                type="integer",
                description="Number of results to return",
                required=False,
                default=10,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute semantic search."""
        query = context.parameters.get("query")
        path = context.parameters.get("path")
        language = context.parameters.get("language")
        top_k = context.parameters.get("top_k", 10)

        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        try:
            # Placeholder for semantic search
            # In production, this would:
            # 1. Generate embedding for query
            # 2. Search vector index
            # 3. Return similar code snippets

            results = []

            # Basic keyword fallback for now
            keywords = query.lower().split()

            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for name in files:
                    if len(results) >= top_k:
                        break

                    if not name.endswith((".py", ".js", ".ts", ".go", ".java")):
                        continue

                    full_path = os.path.join(root, name)
                    rel_path = os.path.relpath(full_path, path)

                    try:
                        with open(
                            full_path, encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        # Simple keyword matching as placeholder
                        score = sum(1 for kw in keywords if kw in content.lower())

                        if score > 0:
                            results.append(
                                {
                                    "file": rel_path,
                                    "score": score / len(keywords),
                                    "snippet": content[:500],
                                }
                            )
                    except Exception:
                        pass

            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:top_k]

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "results": results,
                    "count": len(results),
                    "query": query,
                },
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
