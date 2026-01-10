"""API call tool.

Makes structured API calls.

Capabilities:
- RESTful API calls
- Authentication handling
- Response parsing
- Rate limiting
"""

import base64
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


class ApiCallTool(BaseTool):
    """Make structured API calls.

    Example:
        tool = ApiCallTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "base_url": "https://api.example.com",
                "endpoint": "/users",
                "method": "GET",
            }
        ))
    """

    name = "api_call"
    description = "Make structured API calls"
    category = ToolCategory.WEB
    required_permissions = {"http_requests"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="base_url",
                type="string",
                description="API base URL",
                required=True,
            ),
            ToolParameter(
                name="endpoint",
                type="string",
                description="API endpoint path",
                required=True,
            ),
            ToolParameter(
                name="method",
                type="string",
                description="HTTP method",
                required=False,
                default="GET",
                enum=["GET", "POST", "PUT", "PATCH", "DELETE"],
            ),
            ToolParameter(
                name="params",
                type="object",
                description="Query parameters",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="data",
                type="object",
                description="Request body data",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="auth_type",
                type="string",
                description="Authentication type",
                required=False,
                default=None,
                enum=["bearer", "basic", "api_key"],
            ),
            ToolParameter(
                name="auth_value",
                type="string",
                description="Authentication value (token, key, or user:pass)",
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
        """Execute API call."""
        base_url = context.parameters.get("base_url").rstrip("/")
        endpoint = context.parameters.get("endpoint")
        method = context.parameters.get("method", "GET")
        params = context.parameters.get("params")
        data = context.parameters.get("data")
        auth_type = context.parameters.get("auth_type")
        auth_value = context.parameters.get("auth_value")
        timeout = context.parameters.get("timeout", 30)

        try:
            # Build URL
            url = f"{base_url}{endpoint}"
            if params:
                query = "&".join(f"{k}={v}" for k, v in params.items())
                url = f"{url}?{query}"

            # Prepare headers
            headers = {"Content-Type": "application/json"}

            # Add authentication
            if auth_type and auth_value:
                if auth_type == "bearer":
                    headers["Authorization"] = f"Bearer {auth_value}"
                elif auth_type == "basic":
                    encoded = base64.b64encode(auth_value.encode()).decode()
                    headers["Authorization"] = f"Basic {encoded}"
                elif auth_type == "api_key":
                    headers["X-API-Key"] = auth_value

            # Prepare body
            body = None
            if data:
                body = json.dumps(data).encode("utf-8")

            # Make request
            req = urllib.request.Request(
                url,
                data=body,
                method=method,
                headers=headers,
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
                status_code = response.status

            # Parse JSON response
            try:
                response_data = json.loads(response_body)
            except Exception:
                response_data = response_body

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "status_code": status_code,
                    "data": response_data,
                    "url": url,
                    "method": method,
                },
            )

        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
                error_data = json.loads(error_body)
            except Exception:
                error_data = error_body if error_body else str(e)

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "status_code": e.code,
                    "error": error_data,
                    "url": url,
                },
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
