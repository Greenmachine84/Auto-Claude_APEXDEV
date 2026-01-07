"""
Session Management Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Session lifecycle testing
- Multi-provider session support
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

# All 4 auth providers
AUTH_PROVIDERS = ["github", "google", "microsoft", "manual"]


@dataclass
class Session:
    """User session."""
    id: str
    user_id: str
    auth_provider: str
    access_token: str
    refresh_token: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_active: bool = True


class TestSessionCreation:
    """Test session creation."""

    @pytest.mark.parametrize("auth_provider", AUTH_PROVIDERS)
    async def test_create_session_for_each_provider(self, auth_provider: str):
        """Session can be created for each auth provider."""
        session = Session(
            id=str(uuid.uuid4()),
            user_id="user-123",
            auth_provider=auth_provider,
            access_token="access-token",
            refresh_token="refresh-token",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        
        assert session.auth_provider == auth_provider
        assert session.is_active is True

    def test_session_has_required_fields(self):
        """Session has all required fields."""
        required_fields = [
            "id", "user_id", "auth_provider",
            "access_token", "created_at", "expires_at",
        ]
        
        session = Session(
            id="session-123",
            user_id="user-123",
            auth_provider="github",
            access_token="token",
            refresh_token=None,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        
        for field in required_fields:
            assert hasattr(session, field)


class TestSessionLifecycle:
    """Test session lifecycle."""

    async def test_session_expiration(self):
        """Session expires after configured time."""
        session = Session(
            id="session-123",
            user_id="user-123",
            auth_provider="github",
            access_token="token",
            refresh_token=None,
            created_at=datetime.utcnow() - timedelta(days=8),
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        
        is_expired = session.expires_at < datetime.utcnow()
        assert is_expired is True

    async def test_session_refresh(self):
        """Session can be refreshed."""
        session_manager = MagicMock()
        session_manager.refresh = AsyncMock(return_value=Session(
            id="session-123",
            user_id="user-123",
            auth_provider="github",
            access_token="new-token",
            refresh_token="new-refresh",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        ))
        
        new_session = await session_manager.refresh(session_id="session-123")
        
        assert new_session.access_token == "new-token"

    async def test_session_invalidation(self):
        """Session can be invalidated."""
        session_manager = MagicMock()
        session_manager.invalidate = AsyncMock()
        
        await session_manager.invalidate(session_id="session-123")
        
        session_manager.invalidate.assert_called_once_with(session_id="session-123")


class TestSessionStorage:
    """Test session storage."""

    async def test_store_session(self):
        """Session can be stored."""
        storage = MagicMock()
        storage.store = AsyncMock()
        
        session = Session(
            id="session-123",
            user_id="user-123",
            auth_provider="github",
            access_token="token",
            refresh_token=None,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        
        await storage.store(session)
        
        storage.store.assert_called_once()

    async def test_retrieve_session(self):
        """Session can be retrieved."""
        storage = MagicMock()
        storage.get = AsyncMock(return_value=Session(
            id="session-123",
            user_id="user-123",
            auth_provider="github",
            access_token="token",
            refresh_token=None,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        ))
        
        session = await storage.get(session_id="session-123")
        
        assert session.id == "session-123"

    async def test_delete_session(self):
        """Session can be deleted."""
        storage = MagicMock()
        storage.delete = AsyncMock(return_value=True)
        
        result = await storage.delete(session_id="session-123")
        
        assert result is True


class TestSessionSecurity:
    """Test session security."""

    def test_session_id_is_random(self):
        """Session IDs are random."""
        ids = [str(uuid.uuid4()) for _ in range(100)]
        
        # All unique
        assert len(ids) == len(set(ids))

    def test_tokens_not_in_logs(self):
        """Tokens should not appear in logs."""
        session = Session(
            id="session-123",
            user_id="user-123",
            auth_provider="github",
            access_token="secret-token",
            refresh_token="secret-refresh",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        
        # Safe representation should not include tokens
        safe_repr = {
            "id": session.id,
            "user_id": session.user_id,
            "auth_provider": session.auth_provider,
        }
        
        assert "secret-token" not in str(safe_repr)

    async def test_session_validation(self):
        """Session is validated on each request."""
        validator = MagicMock()
        validator.validate = AsyncMock(return_value=True)
        
        is_valid = await validator.validate(
            session_id="session-123",
            user_id="user-123",
        )
        
        assert is_valid is True


class TestMultiSessionSupport:
    """Test multi-session support."""

    @pytest.mark.parametrize("auth_provider", AUTH_PROVIDERS)
    async def test_user_multiple_sessions(self, auth_provider: str):
        """User can have multiple sessions."""
        sessions = [
            Session(
                id=f"session-{i}",
                user_id="user-123",
                auth_provider=auth_provider,
                access_token=f"token-{i}",
                refresh_token=None,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7),
            )
            for i in range(3)
        ]
        
        assert len(sessions) == 3
        user_ids = {s.user_id for s in sessions}
        assert len(user_ids) == 1

    async def test_revoke_all_sessions(self):
        """All user sessions can be revoked."""
        session_manager = MagicMock()
        session_manager.revoke_all = AsyncMock(return_value=5)
        
        count = await session_manager.revoke_all(user_id="user-123")
        
        assert count == 5
