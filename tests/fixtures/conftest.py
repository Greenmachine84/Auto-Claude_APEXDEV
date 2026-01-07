"""
Shared pytest fixtures for the test suite.

This module provides common fixtures that are automatically available
to all tests in the test suite.
"""

import pytest
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Generator, Optional
from unittest.mock import AsyncMock, MagicMock
import asyncio


# ============================================================================
# Enums and Types
# ============================================================================

class TestEnvironment(Enum):
    """Test environment types."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


class ProviderType(Enum):
    """LLM provider types for testing."""
    COPILOT = "copilot"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_environment() -> TestEnvironment:
    """Provide current test environment."""
    return TestEnvironment.UNIT


@pytest.fixture
def test_config() -> dict:
    """Provide common test configuration."""
    return {
        "debug": True,
        "timeout": 30,
        "max_retries": 3,
        "log_level": "DEBUG",
        "async_timeout": 10.0,
    }


# ============================================================================
# Event Loop Fixtures
# ============================================================================

@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock Provider Fixtures
# ============================================================================

@dataclass
class MockProviderConfig:
    """Configuration for mock LLM provider."""
    provider_type: ProviderType
    model: str = "test-model"
    api_key: str = "test-key"
    base_url: Optional[str] = None
    timeout: float = 30.0


@pytest.fixture
def mock_provider_config() -> MockProviderConfig:
    """Provide mock provider configuration."""
    return MockProviderConfig(
        provider_type=ProviderType.OPENAI,
        model="gpt-4",
        api_key="sk-test-key"
    )


@pytest.fixture
def mock_llm_provider(mock_provider_config: MockProviderConfig) -> MagicMock:
    """Create mock LLM provider."""
    provider = MagicMock()
    provider.config = mock_provider_config
    provider.complete = AsyncMock(return_value="Test response")
    provider.stream = AsyncMock()
    provider.embed = AsyncMock(return_value=[0.1] * 384)
    return provider


# ============================================================================
# Agent Fixtures
# ============================================================================

@dataclass
class AgentConfig:
    """Agent configuration for tests."""
    agent_id: str
    name: str
    provider_type: ProviderType = ProviderType.OPENAI
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: list[str] = None
    system_prompt: str = "You are a helpful assistant."

    def __post_init__(self):
        if self.tools is None:
            self.tools = []


@pytest.fixture
def agent_config() -> AgentConfig:
    """Provide default agent configuration."""
    return AgentConfig(
        agent_id="test-agent-001",
        name="Test Agent",
        tools=["search", "read_file"]
    )


@pytest.fixture
def mock_agent(agent_config: AgentConfig) -> MagicMock:
    """Create mock agent."""
    agent = MagicMock()
    agent.config = agent_config
    agent.id = agent_config.agent_id
    agent.name = agent_config.name
    agent.execute = AsyncMock(return_value={"status": "success"})
    agent.handle_message = AsyncMock(return_value="Response")
    return agent


# ============================================================================
# Memory Fixtures
# ============================================================================

@dataclass
class MemoryEntryData:
    """Test memory entry data."""
    id: str
    content: str
    category: str = "semantic"
    tags: list[str] = None
    embedding: list[float] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@pytest.fixture
def memory_entry_data() -> MemoryEntryData:
    """Provide test memory entry."""
    return MemoryEntryData(
        id="mem-test-001",
        content="This is test memory content",
        tags=["test", "fixture"]
    )


@pytest.fixture
def mock_memory_store() -> MagicMock:
    """Create mock memory store."""
    store = MagicMock()
    store.store = AsyncMock(return_value=True)
    store.retrieve = AsyncMock(return_value=None)
    store.search = AsyncMock(return_value=[])
    store.delete = AsyncMock(return_value=True)
    return store


# ============================================================================
# Tool Fixtures
# ============================================================================

@dataclass
class ToolDefinition:
    """Tool definition for tests."""
    name: str
    description: str
    parameters: dict
    required_permissions: list[str] = None

    def __post_init__(self):
        if self.required_permissions is None:
            self.required_permissions = []


@pytest.fixture
def tool_definition() -> ToolDefinition:
    """Provide test tool definition."""
    return ToolDefinition(
        name="test_tool",
        description="A test tool for fixture testing",
        parameters={
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        }
    )


@pytest.fixture
def mock_tool_executor() -> MagicMock:
    """Create mock tool executor."""
    executor = MagicMock()
    executor.execute = AsyncMock(return_value={"result": "success"})
    executor.validate = MagicMock(return_value=True)
    return executor


# ============================================================================
# Security Fixtures
# ============================================================================

@dataclass
class TestUser:
    """Test user for authentication."""
    id: str
    username: str
    roles: list[str] = None
    permissions: list[str] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = ["user"]
        if self.permissions is None:
            self.permissions = ["read"]


@pytest.fixture
def test_user() -> TestUser:
    """Provide test user."""
    return TestUser(
        id="user-001",
        username="testuser",
        roles=["user", "developer"],
        permissions=["read", "write", "execute"]
    )


@pytest.fixture
def admin_user() -> TestUser:
    """Provide admin test user."""
    return TestUser(
        id="admin-001",
        username="admin",
        roles=["admin"],
        permissions=["read", "write", "execute", "admin"]
    )


@pytest.fixture
def mock_authenticator() -> MagicMock:
    """Create mock authenticator."""
    auth = MagicMock()
    auth.authenticate = AsyncMock(return_value=True)
    auth.get_user = AsyncMock()
    auth.verify_token = MagicMock(return_value=True)
    return auth


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_database() -> MagicMock:
    """Create mock database connection."""
    db = MagicMock()
    db.connect = AsyncMock()
    db.disconnect = AsyncMock()
    db.execute = AsyncMock(return_value=[])
    db.fetch_one = AsyncMock(return_value=None)
    db.fetch_all = AsyncMock(return_value=[])
    return db


# ============================================================================
# HTTP Fixtures
# ============================================================================

@pytest.fixture
def mock_http_client() -> MagicMock:
    """Create mock HTTP client."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Add any global cleanup logic here


# ============================================================================
# Marker Registration
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests requiring external API"
    )
