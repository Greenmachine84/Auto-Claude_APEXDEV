"""
Web Tools - Phase 8 Builtin.

Consolidated web operations.
"""

import logging

import aiohttp

from ..models import (
    ParameterType,
    Tool,
    ToolCategory,
    ToolExecutionContext,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)


class WebTools:
    """Web operation tools."""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Get all web tools."""
        return [
            WebTools._http_get_tool(),
            WebTools._http_post_tool(),
            WebTools._fetch_url_tool(),
        ]

    @staticmethod
    def _http_get_tool() -> Tool:
        return Tool(
            name="http_get",
            description="Make HTTP GET request",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="url", type=ParameterType.URL, description="URL", required=True
                ),
                ToolParameter(
                    name="headers",
                    type=ParameterType.OBJECT,
                    description="Headers",
                    default={},
                ),
            ],
            handler=WebTools.http_get,
            tags=["web", "http", "get"],
        )

    @staticmethod
    def _http_post_tool() -> Tool:
        return Tool(
            name="http_post",
            description="Make HTTP POST request",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="url", type=ParameterType.URL, description="URL", required=True
                ),
                ToolParameter(
                    name="data",
                    type=ParameterType.OBJECT,
                    description="Request body",
                    default={},
                ),
                ToolParameter(
                    name="headers",
                    type=ParameterType.OBJECT,
                    description="Headers",
                    default={},
                ),
            ],
            handler=WebTools.http_post,
            tags=["web", "http", "post"],
        )

    @staticmethod
    def _fetch_url_tool() -> Tool:
        return Tool(
            name="fetch_url",
            description="Fetch URL content",
            category=ToolCategory.WEB,
            parameters=[
                ToolParameter(
                    name="url", type=ParameterType.URL, description="URL", required=True
                ),
            ],
            handler=WebTools.fetch_url,
            tags=["web", "fetch"],
        )

    @staticmethod
    async def http_get(
        ctx: ToolExecutionContext, url: str, headers: dict = None
    ) -> ToolResult:
        """HTTP GET request."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers or {}) as resp:
                    content = await resp.text()
                    return ToolResult(
                        output={"status": resp.status, "body": content},
                        error=None,
                        metadata={"url": url, "status": resp.status},
                    )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"url": url})

    @staticmethod
    async def http_post(
        ctx: ToolExecutionContext, url: str, data: dict = None, headers: dict = None
    ) -> ToolResult:
        """HTTP POST request."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=data or {}, headers=headers or {}
                ) as resp:
                    content = await resp.text()
                    return ToolResult(
                        output={"status": resp.status, "body": content},
                        error=None,
                        metadata={"url": url, "status": resp.status},
                    )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"url": url})

    @staticmethod
    async def fetch_url(ctx: ToolExecutionContext, url: str) -> ToolResult:
        """Fetch URL content."""
        return await WebTools.http_get(ctx, url, {})
