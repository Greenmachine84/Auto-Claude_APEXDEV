"""HTTP request tool.

Makes HTTP requests.

Capabilities:
- GET, POST, PUT, DELETE
- Custom headers
- Request body
- Response handling
"""

import json
import urllib.error
import urllib.request

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)


class HttpRequestTool(BaseTool):
    """Make HTTP requests.

    Example:
        tool = HttpRequestTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "url": "https://api.example.com/data",
                "method": "GET",
            }
        ))
    """

    name = "http_request"
    description = "Make HTTP requests"
    category = ToolCategory.WEB
    required_permissions = {"http_requests"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="url",
                type="string",
                description="URL to request",
                required=True,
            ),
            ToolParameter(
                name="method",
                type="string",
                description="HTTP method",
                required=False,
                default="GET",
                enum=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            ),
            ToolParameter(
                name="headers",
                type="object",
                description="Request headers",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="body",
                type="string",
                description="Request body",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="json_body",
                type="object",
                description="JSON request body",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Timeout in seconds",
                required=False,
                default=30,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute HTTP request."""
        url = context.parameters.get("url")
        method = context.parameters.get("method", "GET")
        headers = context.parameters.get("headers", {})
        body = context.parameters.get("body")
        json_body = context.parameters.get("json_body")
        timeout = context.parameters.get("timeout", 30)

        try:
            # Prepare body
            data = None
            if json_body:
                data = json.dumps(json_body).encode("utf-8")
                headers["Content-Type"] = "application/json"
            elif body:
                data = body.encode("utf-8")

            # Create request
            req = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers=headers,
            )

            # Make request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
                response_headers = dict(response.headers)
                status_code = response.status

            # Try to parse JSON
            try:
                response_json = json.loads(response_body)
            except Exception:
                response_json = None

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "status_code": status_code,
                    "headers": response_headers,
                    "body": response_body,
                    "json": response_json,
                },
            )

        except urllib.error.HTTPError as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "status_code": e.code,
                    "headers": dict(e.headers),
                    "body": e.read().decode("utf-8") if e.fp else "",
                    "error": str(e),
                },
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
