"""
Integration tests for API Endpoints.

Tests the complete API layer including request handling, response formatting,
authentication middleware, and error handling.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from unittest.mock import AsyncMock, MagicMock
import json


class HttpMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HttpStatus(Enum):
    """Common HTTP status codes."""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    TOO_MANY_REQUESTS = 429
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


@dataclass
class ApiRequest:
    """API request representation."""
    method: HttpMethod
    path: str
    headers: dict = field(default_factory=dict)
    query_params: dict = field(default_factory=dict)
    body: Optional[dict] = None
    request_id: str = ""

    def get_header(self, name: str, default: str = "") -> str:
        """Get header case-insensitively."""
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default


@dataclass
class ApiResponse:
    """API response representation."""
    status: HttpStatus
    body: Optional[dict] = None
    headers: dict = field(default_factory=dict)
    content_type: str = "application/json"


@dataclass
class RouteDefinition:
    """API route definition."""
    path: str
    method: HttpMethod
    handler: Callable
    requires_auth: bool = True
    rate_limit: Optional[int] = None


class MockAuthMiddleware:
    """Mock authentication middleware."""

    def __init__(self):
        self._valid_tokens: dict[str, dict] = {}
        self._api_keys: dict[str, dict] = {}

    def register_token(self, token: str, user_data: dict) -> None:
        """Register a valid token."""
        self._valid_tokens[token] = user_data

    def register_api_key(self, api_key: str, metadata: dict) -> None:
        """Register an API key."""
        self._api_keys[api_key] = metadata

    async def authenticate(self, request: ApiRequest) -> tuple[bool, Optional[dict]]:
        """Authenticate a request."""
        # Check Bearer token
        auth_header = request.get_header("Authorization")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token in self._valid_tokens:
                return True, self._valid_tokens[token]

        # Check API key
        api_key = request.get_header("X-API-Key")
        if api_key in self._api_keys:
            return True, self._api_keys[api_key]

        return False, None


class MockRateLimitMiddleware:
    """Mock rate limiting middleware."""

    def __init__(self):
        self._request_counts: dict[str, int] = {}
        self._window_start: dict[str, datetime] = {}
        self._default_limit = 100

    async def check(
        self,
        request: ApiRequest,
        limit: Optional[int] = None
    ) -> tuple[bool, int]:
        """Check if request is within rate limit."""
        key = request.get_header("X-API-Key") or request.get_header("Authorization")
        if not key:
            key = "anonymous"

        effective_limit = limit or self._default_limit
        now = datetime.now()

        # Reset window if needed
        if key not in self._window_start:
            self._window_start[key] = now
            self._request_counts[key] = 0

        self._request_counts[key] += 1
        remaining = max(0, effective_limit - self._request_counts[key])

        if self._request_counts[key] > effective_limit:
            return False, 0

        return True, remaining


class MockValidationMiddleware:
    """Mock request validation middleware."""

    def __init__(self):
        self._schemas: dict[str, dict] = {}

    def register_schema(self, path: str, method: HttpMethod, schema: dict) -> None:
        """Register validation schema for route."""
        key = f"{method.value}:{path}"
        self._schemas[key] = schema

    async def validate(
        self,
        request: ApiRequest
    ) -> tuple[bool, list[str]]:
        """Validate request against schema."""
        key = f"{request.method.value}:{request.path}"
        schema = self._schemas.get(key)

        if not schema:
            return True, []

        errors = []

        # Check required fields
        required = schema.get("required", [])
        if request.body:
            for field_name in required:
                if field_name not in request.body:
                    errors.append(f"Missing required field: {field_name}")

        # Check field types
        properties = schema.get("properties", {})
        if request.body:
            for field_name, field_schema in properties.items():
                if field_name in request.body:
                    expected_type = field_schema.get("type")
                    value = request.body[field_name]

                    if expected_type == "string" and not isinstance(value, str):
                        errors.append(f"Field {field_name} must be string")
                    elif expected_type == "integer" and not isinstance(value, int):
                        errors.append(f"Field {field_name} must be integer")
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        errors.append(f"Field {field_name} must be boolean")

        return len(errors) == 0, errors


class MockApiRouter:
    """Mock API router."""

    def __init__(self):
        self._routes: dict[str, dict[HttpMethod, RouteDefinition]] = {}

    def register(self, route: RouteDefinition) -> None:
        """Register a route."""
        if route.path not in self._routes:
            self._routes[route.path] = {}
        self._routes[route.path][route.method] = route

    def match(self, path: str, method: HttpMethod) -> Optional[RouteDefinition]:
        """Match a path and method to a route."""
        if path in self._routes:
            return self._routes[path].get(method)

        # Check path parameters (simple implementation)
        for route_path, methods in self._routes.items():
            if method not in methods:
                continue

            route_parts = route_path.split("/")
            path_parts = path.split("/")

            if len(route_parts) != len(path_parts):
                continue

            match = True
            for rp, pp in zip(route_parts, path_parts):
                if rp.startswith("{") and rp.endswith("}"):
                    continue
                if rp != pp:
                    match = False
                    break

            if match:
                return methods[method]

        return None

    def get_allowed_methods(self, path: str) -> list[HttpMethod]:
        """Get allowed methods for a path."""
        if path in self._routes:
            return list(self._routes[path].keys())
        return []


class MockApiServer:
    """Mock API server combining all middleware."""

    def __init__(
        self,
        router: MockApiRouter,
        auth: MockAuthMiddleware,
        rate_limit: MockRateLimitMiddleware,
        validation: MockValidationMiddleware
    ):
        self.router = router
        self.auth = auth
        self.rate_limit = rate_limit
        self.validation = validation
        self._request_log: list[dict] = []

    async def handle(self, request: ApiRequest) -> ApiResponse:
        """Handle an API request."""
        self._log_request(request)

        # Find route
        route = self.router.match(request.path, request.method)

        if not route:
            allowed = self.router.get_allowed_methods(request.path)
            if allowed:
                return ApiResponse(
                    status=HttpStatus.METHOD_NOT_ALLOWED,
                    body={"error": "Method not allowed"},
                    headers={"Allow": ", ".join(m.value for m in allowed)}
                )
            return ApiResponse(
                status=HttpStatus.NOT_FOUND,
                body={"error": "Not found"}
            )

        # Rate limiting
        allowed, remaining = await self.rate_limit.check(request, route.rate_limit)
        if not allowed:
            return ApiResponse(
                status=HttpStatus.TOO_MANY_REQUESTS,
                body={"error": "Rate limit exceeded"},
                headers={"X-RateLimit-Remaining": "0"}
            )

        # Authentication
        if route.requires_auth:
            authenticated, user_data = await self.auth.authenticate(request)
            if not authenticated:
                return ApiResponse(
                    status=HttpStatus.UNAUTHORIZED,
                    body={"error": "Unauthorized"}
                )

        # Validation
        valid, errors = await self.validation.validate(request)
        if not valid:
            return ApiResponse(
                status=HttpStatus.BAD_REQUEST,
                body={"error": "Validation failed", "details": errors}
            )

        # Execute handler
        try:
            response = await route.handler(request)
            return response
        except Exception as e:
            return ApiResponse(
                status=HttpStatus.INTERNAL_ERROR,
                body={"error": str(e)}
            )

    def _log_request(self, request: ApiRequest) -> None:
        """Log request for auditing."""
        self._request_log.append({
            "method": request.method.value,
            "path": request.path,
            "timestamp": datetime.now().isoformat()
        })


# ============================================================================
# Mock Handlers
# ============================================================================

async def mock_list_agents(request: ApiRequest) -> ApiResponse:
    """Mock handler for listing agents."""
    return ApiResponse(
        status=HttpStatus.OK,
        body={"agents": ["coder", "reviewer", "fixer"]}
    )


async def mock_get_agent(request: ApiRequest) -> ApiResponse:
    """Mock handler for getting an agent."""
    agent_id = request.path.split("/")[-1]
    return ApiResponse(
        status=HttpStatus.OK,
        body={"id": agent_id, "status": "active"}
    )


async def mock_create_task(request: ApiRequest) -> ApiResponse:
    """Mock handler for creating a task."""
    return ApiResponse(
        status=HttpStatus.CREATED,
        body={"id": "task-123", "status": "created"}
    )


async def mock_health_check(request: ApiRequest) -> ApiResponse:
    """Mock handler for health check."""
    return ApiResponse(
        status=HttpStatus.OK,
        body={"status": "healthy", "timestamp": datetime.now().isoformat()}
    )


# ============================================================================
# Test Classes
# ============================================================================

class TestRouting:
    """Tests for API routing."""

    @pytest.fixture
    def router(self) -> MockApiRouter:
        """Create router with routes."""
        router = MockApiRouter()
        router.register(RouteDefinition(
            path="/api/agents",
            method=HttpMethod.GET,
            handler=mock_list_agents
        ))
        router.register(RouteDefinition(
            path="/api/agents/{id}",
            method=HttpMethod.GET,
            handler=mock_get_agent
        ))
        router.register(RouteDefinition(
            path="/api/tasks",
            method=HttpMethod.POST,
            handler=mock_create_task
        ))
        router.register(RouteDefinition(
            path="/health",
            method=HttpMethod.GET,
            handler=mock_health_check,
            requires_auth=False
        ))
        return router

    def test_exact_path_match(self, router: MockApiRouter):
        """Test exact path matching."""
        route = router.match("/api/agents", HttpMethod.GET)
        assert route is not None
        assert route.handler == mock_list_agents

    def test_parameterized_path_match(self, router: MockApiRouter):
        """Test parameterized path matching."""
        route = router.match("/api/agents/agent-123", HttpMethod.GET)
        assert route is not None
        assert route.handler == mock_get_agent

    def test_no_match_returns_none(self, router: MockApiRouter):
        """Test non-matching path returns None."""
        route = router.match("/api/unknown", HttpMethod.GET)
        assert route is None

    def test_wrong_method_returns_none(self, router: MockApiRouter):
        """Test wrong method returns None."""
        route = router.match("/api/agents", HttpMethod.DELETE)
        assert route is None

    def test_allowed_methods(self, router: MockApiRouter):
        """Test getting allowed methods."""
        methods = router.get_allowed_methods("/api/agents")
        assert HttpMethod.GET in methods


class TestAuthentication:
    """Tests for API authentication."""

    @pytest.fixture
    def auth(self) -> MockAuthMiddleware:
        """Create auth middleware."""
        auth = MockAuthMiddleware()
        auth.register_token("valid-bearer-token", {"user_id": "user1"})
        auth.register_api_key("valid-api-key", {"scope": "full"})
        return auth

    @pytest.mark.asyncio
    async def test_bearer_token_auth(self, auth: MockAuthMiddleware):
        """Test Bearer token authentication."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents",
            headers={"Authorization": "Bearer valid-bearer-token"}
        )

        authenticated, user_data = await auth.authenticate(request)

        assert authenticated is True
        assert user_data["user_id"] == "user1"

    @pytest.mark.asyncio
    async def test_api_key_auth(self, auth: MockAuthMiddleware):
        """Test API key authentication."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents",
            headers={"X-API-Key": "valid-api-key"}
        )

        authenticated, user_data = await auth.authenticate(request)

        assert authenticated is True
        assert user_data["scope"] == "full"

    @pytest.mark.asyncio
    async def test_invalid_token_fails(self, auth: MockAuthMiddleware):
        """Test invalid token fails authentication."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents",
            headers={"Authorization": "Bearer invalid-token"}
        )

        authenticated, user_data = await auth.authenticate(request)

        assert authenticated is False


class TestRateLimiting:
    """Tests for API rate limiting."""

    @pytest.fixture
    def rate_limit(self) -> MockRateLimitMiddleware:
        """Create rate limit middleware."""
        return MockRateLimitMiddleware()

    @pytest.mark.asyncio
    async def test_under_limit_passes(self, rate_limit: MockRateLimitMiddleware):
        """Test requests under limit pass."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents",
            headers={"X-API-Key": "test-key"}
        )

        allowed, remaining = await rate_limit.check(request, limit=10)

        assert allowed is True
        assert remaining == 9

    @pytest.mark.asyncio
    async def test_over_limit_fails(self, rate_limit: MockRateLimitMiddleware):
        """Test requests over limit fail."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents",
            headers={"X-API-Key": "test-key"}
        )

        # Make 5 requests
        for _ in range(5):
            await rate_limit.check(request, limit=5)

        # 6th should fail
        allowed, remaining = await rate_limit.check(request, limit=5)

        assert allowed is False
        assert remaining == 0


class TestValidation:
    """Tests for request validation."""

    @pytest.fixture
    def validation(self) -> MockValidationMiddleware:
        """Create validation middleware."""
        middleware = MockValidationMiddleware()
        middleware.register_schema("/api/tasks", HttpMethod.POST, {
            "required": ["name", "description"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "integer"}
            }
        })
        return middleware

    @pytest.mark.asyncio
    async def test_valid_request_passes(self, validation: MockValidationMiddleware):
        """Test valid request passes validation."""
        request = ApiRequest(
            method=HttpMethod.POST,
            path="/api/tasks",
            body={"name": "Test Task", "description": "A test", "priority": 1}
        )

        valid, errors = await validation.validate(request)

        assert valid is True
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_missing_required_field(self, validation: MockValidationMiddleware):
        """Test missing required field fails."""
        request = ApiRequest(
            method=HttpMethod.POST,
            path="/api/tasks",
            body={"name": "Test Task"}  # Missing description
        )

        valid, errors = await validation.validate(request)

        assert valid is False
        assert any("description" in e for e in errors)

    @pytest.mark.asyncio
    async def test_wrong_type_fails(self, validation: MockValidationMiddleware):
        """Test wrong field type fails."""
        request = ApiRequest(
            method=HttpMethod.POST,
            path="/api/tasks",
            body={"name": "Test", "description": "Test", "priority": "high"}
        )

        valid, errors = await validation.validate(request)

        assert valid is False
        assert any("priority" in e for e in errors)


class TestFullApiServer:
    """Tests for complete API server."""

    @pytest.fixture
    def server(self) -> MockApiServer:
        """Create full API server."""
        router = MockApiRouter()
        router.register(RouteDefinition(
            path="/api/agents",
            method=HttpMethod.GET,
            handler=mock_list_agents
        ))
        router.register(RouteDefinition(
            path="/api/tasks",
            method=HttpMethod.POST,
            handler=mock_create_task,
            rate_limit=10
        ))
        router.register(RouteDefinition(
            path="/health",
            method=HttpMethod.GET,
            handler=mock_health_check,
            requires_auth=False
        ))

        auth = MockAuthMiddleware()
        auth.register_token("valid-token", {"user_id": "user1"})

        validation = MockValidationMiddleware()
        validation.register_schema("/api/tasks", HttpMethod.POST, {
            "required": ["name"]
        })

        return MockApiServer(
            router=router,
            auth=auth,
            rate_limit=MockRateLimitMiddleware(),
            validation=validation
        )

    @pytest.mark.asyncio
    async def test_successful_request(self, server: MockApiServer):
        """Test successful authenticated request."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents",
            headers={"Authorization": "Bearer valid-token"}
        )

        response = await server.handle(request)

        assert response.status == HttpStatus.OK
        assert "agents" in response.body

    @pytest.mark.asyncio
    async def test_unauthenticated_request(self, server: MockApiServer):
        """Test unauthenticated request fails."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/agents"
        )

        response = await server.handle(request)

        assert response.status == HttpStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_public_endpoint(self, server: MockApiServer):
        """Test public endpoint works without auth."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/health"
        )

        response = await server.handle(request)

        assert response.status == HttpStatus.OK
        assert response.body["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_not_found(self, server: MockApiServer):
        """Test not found response."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/unknown",
            headers={"Authorization": "Bearer valid-token"}
        )

        response = await server.handle(request)

        assert response.status == HttpStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, server: MockApiServer):
        """Test method not allowed response."""
        request = ApiRequest(
            method=HttpMethod.DELETE,
            path="/api/agents",
            headers={"Authorization": "Bearer valid-token"}
        )

        response = await server.handle(request)

        assert response.status == HttpStatus.METHOD_NOT_ALLOWED
        assert "Allow" in response.headers

    @pytest.mark.asyncio
    async def test_validation_failure(self, server: MockApiServer):
        """Test validation failure response."""
        request = ApiRequest(
            method=HttpMethod.POST,
            path="/api/tasks",
            headers={"Authorization": "Bearer valid-token"},
            body={}  # Missing required 'name'
        )

        response = await server.handle(request)

        assert response.status == HttpStatus.BAD_REQUEST
        assert "details" in response.body

    @pytest.mark.asyncio
    async def test_request_logging(self, server: MockApiServer):
        """Test requests are logged."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/health"
        )

        await server.handle(request)

        assert len(server._request_log) == 1
        assert server._request_log[0]["path"] == "/health"


class TestErrorHandling:
    """Tests for API error handling."""

    @pytest.fixture
    def server_with_error_handler(self) -> MockApiServer:
        """Create server with error-prone handler."""
        async def error_handler(request: ApiRequest) -> ApiResponse:
            raise RuntimeError("Simulated error")

        router = MockApiRouter()
        router.register(RouteDefinition(
            path="/api/error",
            method=HttpMethod.GET,
            handler=error_handler,
            requires_auth=False
        ))

        return MockApiServer(
            router=router,
            auth=MockAuthMiddleware(),
            rate_limit=MockRateLimitMiddleware(),
            validation=MockValidationMiddleware()
        )

    @pytest.mark.asyncio
    async def test_handler_error_returns_500(self, server_with_error_handler: MockApiServer):
        """Test handler errors return 500."""
        request = ApiRequest(
            method=HttpMethod.GET,
            path="/api/error"
        )

        response = await server_with_error_handler.handle(request)

        assert response.status == HttpStatus.INTERNAL_ERROR
        assert "error" in response.body
