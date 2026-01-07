"""
Shared Mock Classes Package.

This package provides reusable mock implementations for testing
across the entire test suite. These mocks simulate real system
components with configurable behavior.

Mock Categories:
- Providers: Mock LLM providers for all 8 supported backends
- Agents: Mock agents with configurable behavior
- Tools: Mock tool implementations
- Services: Mock external services (HTTP, database, etc.)
"""

from .mock_providers import (
    MockLLMProvider,
    MockProviderFactory,
    MockProviderRegistry,
    MockStreamingProvider,
)
from .mock_agents import (
    MockAgent,
    MockCoderAgent,
    MockReviewerAgent,
    MockAgentFactory,
    MockAgentOrchestrator,
)
from .mock_tools import (
    MockTool,
    MockToolExecutor,
    MockToolRegistry,
    MockSandboxedTool,
)
from .mock_services import (
    MockHttpClient,
    MockDatabase,
    MockCache,
    MockMessageQueue,
    MockFileSystem,
)

__all__ = [
    # Providers
    "MockLLMProvider",
    "MockProviderFactory",
    "MockProviderRegistry",
    "MockStreamingProvider",
    # Agents
    "MockAgent",
    "MockCoderAgent",
    "MockReviewerAgent",
    "MockAgentFactory",
    "MockAgentOrchestrator",
    # Tools
    "MockTool",
    "MockToolExecutor",
    "MockToolRegistry",
    "MockSandboxedTool",
    # Services
    "MockHttpClient",
    "MockDatabase",
    "MockCache",
    "MockMessageQueue",
    "MockFileSystem",
]
