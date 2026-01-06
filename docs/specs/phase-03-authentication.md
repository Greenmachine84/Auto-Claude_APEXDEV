# Phase 3: Authentication

> **Duration**: Week 5-6 | **Priority**: ⚠️ CRITICAL
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| GitHub OAuth works | Login flow completes | ✅ |
| Google OAuth works | Login flow completes | ✅ |
| Microsoft OAuth works | Login flow completes | ✅ |
| Manual signup works | Account creation works | ✅ |
| Sessions persist | Refresh tokens work | ✅ |
| LLM credentials stored | Per-user encrypted storage | ✅ |

### Deliverables

1. `apps/backend/auth/providers/base_auth.py`
2. `apps/backend/auth/providers/github_auth.py`
3. `apps/backend/auth/providers/google_auth.py`
4. `apps/backend/auth/providers/microsoft_auth.py`
5. `apps/backend/auth/providers/manual_auth.py`
6. `apps/backend/auth/session/session_manager.py`
7. `apps/backend/auth/user/user_service.py`
8. `apps/backend/auth/user/credentials.py`
9. Database migrations for users table
10. Unit tests for all modules

---

## Section 1: Auth Provider Abstraction

### Task 1.1: Create Auth Directory Structure

**Directory Structure**:
```
apps/backend/auth/
├── __init__.py
├── providers/
│   ├── __init__.py
│   ├── base_auth.py
│   ├── github_auth.py
│   ├── google_auth.py
│   ├── microsoft_auth.py
│   └── manual_auth.py
├── session/
│   ├── __init__.py
│   ├── session_manager.py
│   └── token_manager.py
├── user/
│   ├── __init__.py
│   ├── user_service.py
│   ├── profile.py
│   └── credentials.py
└── models.py
```

---

### Task 1.2: Create Auth Models

**File**: `apps/backend/auth/models.py`

```python
"""Authentication models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class AuthProvider(Enum):
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    MANUAL = "manual"

@dataclass
class User:
    """User account."""
    id: str
    email: str
    display_name: str
    auth_provider: AuthProvider
    provider_id: Optional[str] = None  # OAuth provider's user ID
    avatar_url: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

@dataclass
class Session:
    """User session."""
    id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: str = ""
    created_at: str = ""
    device_info: Optional[str] = None

@dataclass
class AuthResult:
    """Result of authentication attempt."""
    success: bool
    user: Optional[User] = None
    session: Optional[Session] = None
    error: Optional[str] = None

@dataclass
class TokenPair:
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    expires_in: int  # seconds
```

---

### Task 1.3: Create Base Auth Provider

**File**: `apps/backend/auth/providers/base_auth.py`

```python
"""Abstract base class for authentication providers."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..models import User, AuthResult, TokenPair

class BaseAuthProvider(ABC):
    """Abstract base for all auth providers."""
    
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        self._configured = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure with OAuth credentials.
        
        Args:
            config: client_id, client_secret, redirect_uri, etc.
        """
        pass
    
    @abstractmethod
    async def get_auth_url(self, state: str) -> str:
        """Get OAuth authorization URL.
        
        Args:
            state: CSRF protection state
            
        Returns:
            URL to redirect user to
        """
        pass
    
    @abstractmethod
    async def handle_callback(
        self, 
        code: str, 
        state: str
    ) -> AuthResult:
        """Handle OAuth callback.
        
        Args:
            code: Authorization code from provider
            state: CSRF state to verify
            
        Returns:
            AuthResult with user info
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh expired access token."""
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> User:
        """Get user profile from provider."""
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Revoke access token (logout)."""
        pass
```

---

## Section 2: OAuth Providers

### Task 2.1: GitHub OAuth Provider

**File**: `apps/backend/auth/providers/github_auth.py`

```python
"""GitHub OAuth provider."""
import httpx
from typing import Dict, Any
from .base_auth import BaseAuthProvider
from ..models import User, AuthResult, TokenPair, AuthProvider

class GitHubAuthProvider(BaseAuthProvider):
    """GitHub OAuth 2.0 implementation."""
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_URL = "https://api.github.com"
    
    def __init__(self):
        super().__init__("github")
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
    
    @property
    def name(self) -> str:
        return "GitHub"
    
    async def configure(self, config: Dict[str, Any]) -> bool:
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self._configured = all([
            self.client_id, 
            self.client_secret, 
            self.redirect_uri
        ])
        return self._configured
    
    async def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"
    
    async def handle_callback(self, code: str, state: str) -> AuthResult:
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"}
            )
            token_data = resp.json()
            
            if "error" in token_data:
                return AuthResult(
                    success=False,
                    error=token_data.get("error_description", "OAuth failed")
                )
            
            # Get user info
            user = await self.get_user_info(token_data["access_token"])
            
            return AuthResult(
                success=True,
                user=user,
            )
    
    async def get_user_info(self, access_token: str) -> User:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.API_URL}/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            data = resp.json()
            
            # Get email if not public
            email = data.get("email")
            if not email:
                email_resp = await client.get(
                    f"{self.API_URL}/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                emails = email_resp.json()
                primary = next((e for e in emails if e["primary"]), None)
                email = primary["email"] if primary else None
            
            return User(
                id="",  # Will be set by user service
                email=email or "",
                display_name=data.get("name") or data.get("login"),
                auth_provider=AuthProvider.GITHUB,
                provider_id=str(data["id"]),
                avatar_url=data.get("avatar_url"),
            )
    
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        # GitHub doesn't use refresh tokens by default
        raise NotImplementedError("GitHub OAuth doesn't support refresh")
    
    async def revoke_token(self, token: str) -> bool:
        # GitHub token revocation
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.API_URL}/applications/{self.client_id}/token",
                auth=(self.client_id, self.client_secret),
                json={"access_token": token}
            )
            return resp.status_code == 204
```

---

### Task 2.2: Google OAuth Provider

**File**: `apps/backend/auth/providers/google_auth.py`

**Key endpoints**:
- Auth: `https://accounts.google.com/o/oauth2/v2/auth`
- Token: `https://oauth2.googleapis.com/token`
- User: `https://www.googleapis.com/oauth2/v2/userinfo`

---

### Task 2.3: Microsoft OAuth Provider

**File**: `apps/backend/auth/providers/microsoft_auth.py`

**Key endpoints**:
- Auth: `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
- Token: `https://login.microsoftonline.com/common/oauth2/v2.0/token`
- User: `https://graph.microsoft.com/v1.0/me`

---

### Task 2.4: Manual Auth Provider

**File**: `apps/backend/auth/providers/manual_auth.py`

**Features**:
- Email/password registration
- Password hashing (bcrypt)
- Email verification
- Password reset

---

## Section 3: Session Management

### Task 3.1: Session Manager

**File**: `apps/backend/auth/session/session_manager.py`

```python
"""Session management."""
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from ..models import Session, User

class SessionManager:
    """Manages user sessions."""
    
    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    device_info TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON sessions(user_id)
            """)
    
    async def create(self, user: User, expires_hours: int = 168) -> Session:
        """Create new session for user (default 7 days)."""
        session = Session(
            id=secrets.token_urlsafe(32),
            user_id=user.id,
            access_token=secrets.token_urlsafe(64),
            refresh_token=secrets.token_urlsafe(64),
            expires_at=(datetime.utcnow() + timedelta(hours=expires_hours)).isoformat(),
            created_at=datetime.utcnow().isoformat(),
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions 
                (id, user_id, access_token, refresh_token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.user_id,
                session.access_token,
                session.refresh_token,
                session.expires_at,
                session.created_at,
            ))
        
        return session
    
    async def validate(self, access_token: str) -> Optional[Session]:
        """Validate access token, return session if valid."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE access_token = ?",
                (access_token,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Check expiry
            expires_at = datetime.fromisoformat(row["expires_at"])
            if datetime.utcnow() > expires_at:
                await self.delete(row["id"])
                return None
            
            return Session(
                id=row["id"],
                user_id=row["user_id"],
                access_token=row["access_token"],
                refresh_token=row["refresh_token"],
                expires_at=row["expires_at"],
                created_at=row["created_at"],
            )
    
    async def delete(self, session_id: str) -> bool:
        """Delete session (logout)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return True
```

---

## Section 4: User Service

### Task 4.1: User Service

**File**: `apps/backend/auth/user/user_service.py`

---

### Task 4.2: LLM Credentials Storage

**File**: `apps/backend/auth/user/credentials.py`

```python
"""Per-user LLM credential storage."""
import sqlite3
from typing import Optional, Dict
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import os

class UserCredentialsManager:
    """Stores user's LLM provider credentials (encrypted)."""
    
    def __init__(self, db_path: str = "user_credentials.db"):
        self.db_path = Path(db_path)
        self._key = self._get_or_create_key()
        self._fernet = Fernet(self._key)
        self._init_db()
    
    def _get_or_create_key(self) -> bytes:
        key_file = Path(".credentials_key")
        if key_file.exists():
            return key_file.read_bytes()
        key = Fernet.generate_key()
        key_file.write_bytes(key)
        return key
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    encrypted_key TEXT NOT NULL,
                    created_at TEXT,
                    UNIQUE(user_id, provider)
                )
            """)
    
    async def store(
        self, 
        user_id: str, 
        provider: str, 
        api_key: str
    ) -> bool:
        """Store encrypted API key for provider."""
        encrypted = self._fernet.encrypt(api_key.encode()).decode()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO credentials 
                (user_id, provider, encrypted_key, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (user_id, provider, encrypted))
        return True
    
    async def get(self, user_id: str, provider: str) -> Optional[str]:
        """Get decrypted API key for provider."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT encrypted_key FROM credentials WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._fernet.decrypt(row[0].encode()).decode()
    
    async def list_providers(self, user_id: str) -> list:
        """List providers user has configured."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT provider FROM credentials WHERE user_id = ?",
                (user_id,)
            )
            return [row[0] for row in cursor.fetchall()]
    
    async def delete(self, user_id: str, provider: str) -> bool:
        """Delete stored credential."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM credentials WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            )
        return True
```

---

## Validation Checklist

- [ ] GitHub OAuth login works end-to-end
- [ ] Google OAuth login works end-to-end
- [ ] Microsoft OAuth login works end-to-end
- [ ] Manual signup creates account
- [ ] Sessions persist across restarts
- [ ] LLM credentials stored encrypted
- [ ] Token refresh works
- [ ] Logout invalidates session
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 1 (Foundation), Phase 2 (LLM Agnostic)

**Enables**: Phase 4 (Orchestration), Phase 6 (Security)

---

## ADR References

- ADR-012: Multi-Provider Authentication
- ADR-010: Security Model Harmonization

---

*Phase 3 Specification v1.0.0*
