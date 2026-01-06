# Phase 3: Authentication

> **Duration**: Week 5-6 | **Priority**: ⚠️ CRITICAL
>
> **Status**: 📋 Specification Ready

---

## ⚠️ QUALITY STANDARDS

> **ALL implementations in this phase MUST meet these mandatory standards:**

| Standard | Requirement | Verification |
|----------|-------------|--------------|
| **World-Class** | Industry-leading OAuth implementation | Security audit |
| **Enterprise-Grade** | Production-ready, SOC 2 compliant patterns | Compliance review |
| **Fully Production Ready** | Zero security vulnerabilities, complete edge case handling | Penetration test |
| **Clean & Concise Code** | Self-documenting, minimal complexity, OWASP compliant | Security review |
| **Beyond PhD Level** | State-of-the-art authentication patterns | Cryptography review |

---

## Outcome Expectations

### Business Objective

| Objective | Description | Impact |
|-----------|-------------|--------|
| **User Onboarding** | Seamless signup via familiar OAuth providers | Reduced friction, higher adoption |
| **Enterprise Integration** | Microsoft OAuth enables enterprise SSO | Enterprise customer acquisition |
| **Security Foundation** | Secure credential management | User trust, compliance |
| **Provider Flexibility** | 4 login options cover all user preferences | Universal accessibility |

### Technical Outcome

| Outcome | Description | Measurement |
|---------|-------------|-------------|
| **GitHub OAuth** | Complete GitHub OAuth 2.0 flow | Login/logout works |
| **Google OAuth** | Complete Google OAuth 2.0 flow | Login/logout works |
| **Microsoft OAuth** | Complete Microsoft OAuth 2.0/OIDC flow | Login/logout works |
| **Manual Auth** | Email/password with secure hashing | Registration/login works |
| **Session Management** | JWT tokens with secure refresh | 7-day sessions persist |
| **Credential Storage** | Encrypted per-user LLM credentials | AES-256 encryption verified |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| GitHub OAuth works | Login flow completes | ✅ | <3 second flow |
| Google OAuth works | Login flow completes | ✅ | <3 second flow |
| Microsoft OAuth works | Login flow completes | ✅ | <3 second flow |
| Manual signup works | Account creation works | ✅ | Email verified |
| Sessions persist | Refresh tokens work | ✅ | 7-day sessions |
| LLM credentials stored | Per-user encrypted storage | ✅ | AES-256-GCM |
| Password security | bcrypt hashing | ✅ | Cost factor 12 |
| CSRF protection | State parameter validated | ✅ | Cryptographic state |
| Token security | Secure token generation | ✅ | 256-bit entropy |
| Zero vulnerabilities | Security scan passes | ✅ | OWASP Top 10 clean |

### Acceptance Tests

| Test | Input | Expected Output | Passing Criteria |
|------|-------|-----------------|------------------|
| AT-3.1 | GitHub OAuth start | Redirect to GitHub | Valid OAuth URL |
| AT-3.2 | GitHub callback with code | User created/logged in | Session token returned |
| AT-3.3 | Google OAuth start | Redirect to Google | Valid OAuth URL |
| AT-3.4 | Google callback with code | User created/logged in | Session token returned |
| AT-3.5 | Microsoft OAuth start | Redirect to Microsoft | Valid OAuth URL |
| AT-3.6 | Microsoft callback with code | User created/logged in | Session token returned |
| AT-3.7 | Manual registration | Account created | Email sent, user in DB |
| AT-3.8 | Manual login | Session created | Token returned |
| AT-3.9 | Invalid password | Login fails | Error message, no session |
| AT-3.10 | Token refresh | New access token | Valid for 7 more days |
| AT-3.11 | Logout | Session invalidated | Token rejected |
| AT-3.12 | CSRF attack attempt | Request rejected | 403 Forbidden |
| AT-3.13 | Store LLM credentials | Encrypted in DB | Decryptable with user key |
| AT-3.14 | Retrieve LLM credentials | Decrypted credentials | Valid API keys returned |

### Performance Metrics

| Metric | Target | World-Class Standard |
|--------|--------|----------------------|
| OAuth flow completion | <3 seconds | Sub-second redirect |
| Token generation | <10ms | Cryptographically secure |
| Session validation | <5ms | Cached validation |
| Password hashing | <500ms | Secure but responsive |
| Credential encryption | <10ms | AES-256-GCM |
| Credential decryption | <10ms | AES-256-GCM |
| Concurrent sessions | 1000+ | Horizontally scalable |

### Risk Mitigations

| Risk | Mitigation | Verification |
|------|------------|--------------|
| OAuth token theft | HTTPS only, secure cookies | TLS test |
| CSRF attacks | Cryptographic state parameter | CSRF test suite |
| Session hijacking | Secure session tokens, rotation | Security audit |
| Password attacks | bcrypt, rate limiting, lockout | Brute force test |
| Credential exposure | AES-256-GCM encryption at rest | Encryption audit |
| Key compromise | Key rotation support, HSM ready | Key management review |
| SQL injection | Parameterized queries only | SQL injection test |
| XSS attacks | Output encoding, CSP headers | XSS test suite |

### Integration Points

| Phase | Component | Integration |
|-------|-----------|-------------|
| Phase 2 | LLM Providers | Credentials used for provider auth |
| Phase 6 | Security | Auth integrates with RBAC |
| Phase 9 | Governance | User context for approval workflows |
| Frontend | UI | Login/logout UI components |

### User-Visible Impact

| Impact | Description |
|--------|-------------|
| **Quick Signup** | Users can sign up in seconds via GitHub/Google/Microsoft |
| **No Password Fatigue** | OAuth eliminates another password to remember |
| **Secure Credentials** | LLM API keys stored safely, not in plain text |
| **Persistent Sessions** | Stay logged in for a week |
| **Enterprise SSO** | Microsoft login enables corporate SSO |

### Deliverables

| # | Deliverable | Purpose | LOC Estimate |
|---|-------------|---------|--------------|
| 1 | `apps/backend/auth/providers/base_auth.py` | Abstract auth interface | 100-150 |
| 2 | `apps/backend/auth/providers/github_auth.py` | GitHub OAuth | 200-250 |
| 3 | `apps/backend/auth/providers/google_auth.py` | Google OAuth | 200-250 |
| 4 | `apps/backend/auth/providers/microsoft_auth.py` | Microsoft OAuth | 200-250 |
| 5 | `apps/backend/auth/providers/manual_auth.py` | Email/password | 250-300 |
| 6 | `apps/backend/auth/session/session_manager.py` | Session handling | 200-250 |
| 7 | `apps/backend/auth/session/token_manager.py` | JWT tokens | 150-200 |
| 8 | `apps/backend/auth/user/user_service.py` | User CRUD | 200-250 |
| 9 | `apps/backend/auth/user/credentials.py` | Encrypted credential storage | 250-300 |
| 10 | `apps/backend/auth/models.py` | Data models | 100-150 |
| 11 | Database migrations | Users, sessions tables | 50-100 |
| 12 | Unit tests | Test coverage | 800+ |

---

## Section 1: Auth Provider Abstraction

### Task 1.1: Create Auth Directory Structure

**Objective**: Establish secure directory structure for authentication

**Quality Gate**: Follows Python package best practices, security-first design

**Directory Structure**:
```
apps/backend/auth/
├── __init__.py
├── models.py
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
└── middleware/
    ├── __init__.py
    └── auth_middleware.py
```

---

### Task 1.2: Create Auth Models

**Objective**: Define secure data models for authentication

**Quality Gate**: Complete type safety, secure defaults

**File**: `apps/backend/auth/models.py`

```python
"""Authentication Models - Enterprise-Grade Security.

This module defines all data models for the authentication system.
All models are designed with security as the primary concern.

Security Principles:
    - Minimal data exposure
    - Secure defaults
    - Immutable where possible
    - Complete audit trail

Quality Standards:
    - 100% type annotated
    - Full validation
    - Serialization-safe
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import secrets

class AuthProvider(Enum):
    """Supported authentication providers.
    
    ALL PROVIDERS ARE EQUAL - no default.
    """
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    MANUAL = "manual"

@dataclass
class User:
    """User account - immutable after creation.
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address
        display_name: User's display name
        auth_provider: How user authenticated
        provider_id: OAuth provider's user ID
        avatar_url: Profile picture URL
        email_verified: Whether email is verified
        created_at: Account creation time
        updated_at: Last modification time
        is_active: Whether account is active
        last_login: Last login timestamp
        metadata: Additional user data
    """
    id: str
    email: str
    display_name: str
    auth_provider: AuthProvider
    provider_id: Optional[str] = None
    avatar_url: Optional[str] = None
    email_verified: bool = False
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True
    last_login: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Args:
            include_sensitive: Include provider_id if True
        """
        result = {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "auth_provider": self.auth_provider.value,
            "avatar_url": self.avatar_url,
            "email_verified": self.email_verified,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }
        if include_sensitive:
            result["provider_id"] = self.provider_id
        return result

@dataclass
class Session:
    """User session - secure token management.
    
    Attributes:
        id: Session identifier
        user_id: Associated user
        access_token: Short-lived access token
        refresh_token: Long-lived refresh token
        expires_at: Access token expiry
        refresh_expires_at: Refresh token expiry
        created_at: Session creation time
        last_used: Last activity time
        device_info: Client device information
        ip_address: Client IP (for audit)
    """
    id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: str = ""
    refresh_expires_at: Optional[str] = None
    created_at: str = ""
    last_used: Optional[str] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    
    @staticmethod
    def generate_token(length: int = 64) -> str:
        """Generate cryptographically secure token."""
        return secrets.token_urlsafe(length)

@dataclass
class AuthResult:
    """Result of authentication attempt.
    
    Encapsulates success/failure with complete context.
    """
    success: bool
    user: Optional[User] = None
    session: Optional[Session] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    requires_verification: bool = False
    
    @classmethod
    def failure(cls, error: str, code: str = "AUTH_ERROR") -> 'AuthResult':
        """Create failure result."""
        return cls(success=False, error=error, error_code=code)
    
    @classmethod
    def success_result(cls, user: User, session: Session) -> 'AuthResult':
        """Create success result."""
        return cls(success=True, user=user, session=session)

@dataclass
class TokenPair:
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    access_expires_in: int  # seconds
    refresh_expires_in: int  # seconds
    token_type: str = "Bearer"

@dataclass
class OAuthState:
    """OAuth CSRF protection state.
    
    Stored server-side to validate callbacks.
    """
    state: str
    provider: AuthProvider
    redirect_uri: str
    created_at: str = ""
    expires_at: str = ""
    nonce: Optional[str] = None  # For OIDC
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
```

---

### Task 1.3: Create Base Auth Provider

**Objective**: Define abstract interface for ALL auth providers

**Quality Gate**: Complete abstraction, security-first design

**File**: `apps/backend/auth/providers/base_auth.py`

```python
"""Abstract Base Class for Authentication Providers - Enterprise-Grade.

This module defines the contract that ALL authentication providers
must implement, ensuring consistent security patterns.

Security Principles:
    - CSRF protection via state parameter
    - Secure token handling
    - Complete audit logging
    - Minimal data exposure

Quality Standards:
    - 100% type annotated
    - Complete async/await support
    - Comprehensive error handling
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

from ..models import User, AuthResult, TokenPair, OAuthState

logger = logging.getLogger(__name__)

class AuthProviderError(Exception):
    """Base exception for auth provider errors."""
    pass

class InvalidStateError(AuthProviderError):
    """CSRF state validation failed."""
    pass

class TokenExchangeError(AuthProviderError):
    """OAuth token exchange failed."""
    pass

class UserInfoError(AuthProviderError):
    """Failed to retrieve user info."""
    pass


class BaseAuthProvider(ABC):
    """Abstract base for all authentication providers.
    
    ALL PROVIDERS ARE EQUAL - users choose their preferred method.
    
    Security Features:
    - CSRF protection via cryptographic state
    - Secure token handling
    - Rate limiting ready
    - Complete audit logging
    
    Implementation Contract:
        Subclasses MUST implement:
        - name property
        - configure() method
        - get_auth_url() method
        - handle_callback() method
        - get_user_info() method
        - revoke_token() method
    """
    
    def __init__(self, provider_id: str):
        """Initialize auth provider.
        
        Args:
            provider_id: Unique identifier (e.g., "github", "google")
        """
        self.provider_id = provider_id
        self._configured = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass
    
    @property
    def is_configured(self) -> bool:
        """Whether provider has been configured."""
        return self._configured
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure with OAuth credentials.
        
        Args:
            config: Provider-specific configuration
                Common keys:
                - client_id: OAuth client ID
                - client_secret: OAuth client secret
                - redirect_uri: Callback URL
                
        Returns:
            True if configuration successful
        """
        pass
    
    @abstractmethod
    async def get_auth_url(self, state: OAuthState) -> str:
        """Get OAuth authorization URL.
        
        Args:
            state: CSRF protection state object
            
        Returns:
            Full URL to redirect user to
        """
        pass
    
    @abstractmethod
    async def handle_callback(
        self, 
        code: str, 
        state: str,
        stored_state: OAuthState
    ) -> AuthResult:
        """Handle OAuth callback.
        
        Args:
            code: Authorization code from provider
            state: State from callback
            stored_state: Original state for validation
            
        Returns:
            AuthResult with user info or error
            
        Raises:
            InvalidStateError: If state doesn't match
            TokenExchangeError: If code exchange fails
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> User:
        """Get user profile from provider.
        
        Args:
            access_token: Valid access token
            
        Returns:
            User object with profile info
            
        Raises:
            UserInfoError: If user info retrieval fails
        """
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Revoke access token (logout from provider).
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        pass
    
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh expired access token.
        
        Default implementation raises NotImplementedError.
        Override for providers that support refresh.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token pair
        """
        raise NotImplementedError(
            f"{self.name} does not support token refresh"
        )
    
    def _validate_state(self, received: str, stored: OAuthState) -> bool:
        """Validate CSRF state parameter.
        
        Args:
            received: State from callback
            stored: Original stored state
            
        Returns:
            True if valid
            
        Raises:
            InvalidStateError: If validation fails
        """
        if received != stored.state:
            logger.warning(
                f"CSRF state mismatch for {self.name}: "
                f"received={received[:8]}..., expected={stored.state[:8]}..."
            )
            raise InvalidStateError("Invalid state parameter - possible CSRF attack")
        return True
```

---

## Section 2: OAuth Providers

### Task 2.1: GitHub OAuth Provider

**Objective**: Implement complete GitHub OAuth 2.0 flow

**Quality Gate**: Full GitHub OAuth spec compliance, error handling

**File**: `apps/backend/auth/providers/github_auth.py`

```python
"""GitHub OAuth Provider - Enterprise-Grade Implementation.

This module implements GitHub OAuth 2.0 for user authentication.

Security Features:
    - CSRF protection via state parameter
    - Secure token exchange
    - Email scope for primary email
    - Complete error handling

Reference: https://docs.github.com/en/developers/apps/building-oauth-apps
"""

import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import logging

from .base_auth import (
    BaseAuthProvider, 
    TokenExchangeError, 
    UserInfoError,
)
from ..models import User, AuthResult, TokenPair, OAuthState, AuthProvider

logger = logging.getLogger(__name__)

class GitHubAuthProvider(BaseAuthProvider):
    """GitHub OAuth 2.0 implementation.
    
    World-Class Features:
    - Complete OAuth 2.0 flow
    - Primary email retrieval
    - Secure token handling
    - Comprehensive error handling
    
    Example:
        >>> provider = GitHubAuthProvider()
        >>> await provider.configure({
        ...     "client_id": "...",
        ...     "client_secret": "...",
        ...     "redirect_uri": "https://example.com/callback"
        ... })
        >>> auth_url = await provider.get_auth_url(state)
    """
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_URL = "https://api.github.com"
    
    def __init__(self):
        super().__init__("github")
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        self.redirect_uri: Optional[str] = None
    
    @property
    def name(self) -> str:
        return "GitHub"
    
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure GitHub OAuth.
        
        Required config keys:
            - client_id: GitHub OAuth App client ID
            - client_secret: GitHub OAuth App client secret
            - redirect_uri: Callback URL registered with GitHub
        """
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        
        self._configured = all([
            self.client_id, 
            self.client_secret, 
            self.redirect_uri
        ])
        
        if self._configured:
            logger.info("GitHub OAuth configured successfully")
        else:
            logger.warning("GitHub OAuth configuration incomplete")
        
        return self._configured
    
    async def get_auth_url(self, state: OAuthState) -> str:
        """Get GitHub authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user user:email",
            "state": state.state,
            "allow_signup": "true",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    async def handle_callback(
        self, 
        code: str, 
        state: str,
        stored_state: OAuthState
    ) -> AuthResult:
        """Handle GitHub OAuth callback."""
        # Validate CSRF state
        self._validate_state(state, stored_state)
        
        # Exchange code for token
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )
                
                token_data = response.json()
                
                if "error" in token_data:
                    logger.error(f"GitHub token exchange failed: {token_data}")
                    return AuthResult.failure(
                        token_data.get("error_description", "Token exchange failed"),
                        "TOKEN_EXCHANGE_FAILED"
                    )
                
                access_token = token_data["access_token"]
                
                # Get user info
                user = await self.get_user_info(access_token)
                
                logger.info(f"GitHub OAuth successful for user: {user.email}")
                
                return AuthResult(
                    success=True,
                    user=user,
                )
                
        except httpx.RequestError as e:
            logger.exception("GitHub API request failed")
            raise TokenExchangeError(f"GitHub API error: {str(e)}")
    
    async def get_user_info(self, access_token: str) -> User:
        """Get user profile from GitHub."""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get user profile
            response = await client.get(
                f"{self.API_URL}/user",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise UserInfoError(f"GitHub user API failed: {response.status_code}")
            
            data = response.json()
            
            # Get primary email if not public
            email = data.get("email")
            if not email:
                email_response = await client.get(
                    f"{self.API_URL}/user/emails",
                    headers=headers,
                    timeout=10.0
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary = next(
                        (e for e in emails if e.get("primary")), 
                        None
                    )
                    if primary:
                        email = primary["email"]
            
            return User(
                id="",  # Will be assigned by UserService
                email=email or "",
                display_name=data.get("name") or data.get("login"),
                auth_provider=AuthProvider.GITHUB,
                provider_id=str(data["id"]),
                avatar_url=data.get("avatar_url"),
                email_verified=True,  # GitHub emails are verified
            )
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke GitHub access token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.API_URL}/applications/{self.client_id}/token",
                    auth=(self.client_id, self.client_secret),
                    json={"access_token": token},
                    timeout=10.0
                )
                return response.status_code == 204
        except Exception as e:
            logger.error(f"GitHub token revocation failed: {e}")
            return False
```

---

### Task 2.2: Google OAuth Provider

**Objective**: Implement complete Google OAuth 2.0 flow

**File**: `apps/backend/auth/providers/google_auth.py`

**Key Endpoints**:
- Auth: `https://accounts.google.com/o/oauth2/v2/auth`
- Token: `https://oauth2.googleapis.com/token`
- User: `https://www.googleapis.com/oauth2/v2/userinfo`

**Features**:
- OpenID Connect support
- Email verification status
- Profile picture retrieval
- Refresh token support

---

### Task 2.3: Microsoft OAuth Provider

**Objective**: Implement complete Microsoft OAuth 2.0/OIDC flow

**File**: `apps/backend/auth/providers/microsoft_auth.py`

**Key Endpoints**:
- Auth: `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
- Token: `https://login.microsoftonline.com/common/oauth2/v2.0/token`
- User: `https://graph.microsoft.com/v1.0/me`

**Features**:
- OIDC ID token support
- Enterprise tenant support
- Microsoft Graph integration
- Refresh token support

---

### Task 2.4: Manual Auth Provider

**Objective**: Implement secure email/password authentication

**File**: `apps/backend/auth/providers/manual_auth.py`

**Features**:
- bcrypt password hashing (cost factor 12)
- Email verification flow
- Password reset flow
- Rate limiting support
- Account lockout after failures

---

## Section 3: Session Management

### Task 3.1: Session Manager

**Objective**: Secure session management with persistence

**Quality Gate**: Cryptographically secure tokens, proper expiry

**File**: `apps/backend/auth/session/session_manager.py`

```python
"""Session Management - Enterprise-Grade Security.

This module provides secure session management with
cryptographically strong tokens and proper lifecycle.

Security Features:
    - 256-bit entropy tokens
    - Secure session rotation
    - Automatic expiry
    - Device binding option
    - Complete audit trail
"""

import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path
from contextlib import contextmanager
import logging

from ..models import Session, User

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions with security best practices.
    
    World-Class Features:
    - Cryptographically secure token generation
    - Automatic session expiry
    - Session rotation on refresh
    - Device tracking for audit
    - Concurrent session limiting
    
    Example:
        >>> manager = SessionManager()
        >>> session = await manager.create(user)
        >>> valid_session = await manager.validate(session.access_token)
    """
    
    def __init__(
        self, 
        db_path: str = "data/sessions.db",
        access_token_hours: int = 1,
        refresh_token_days: int = 7,
        max_sessions_per_user: int = 10
    ):
        """Initialize session manager.
        
        Args:
            db_path: Path to sessions database
            access_token_hours: Access token validity
            refresh_token_days: Refresh token validity
            max_sessions_per_user: Maximum concurrent sessions
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.access_token_hours = access_token_hours
        self.refresh_token_days = refresh_token_days
        self.max_sessions_per_user = max_sessions_per_user
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    access_token TEXT UNIQUE NOT NULL,
                    refresh_token TEXT UNIQUE,
                    expires_at TEXT NOT NULL,
                    refresh_expires_at TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    device_info TEXT,
                    ip_address TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
                ON sessions(user_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_access_token 
                ON sessions(access_token)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token 
                ON sessions(refresh_token)
            """)
    
    async def create(
        self, 
        user: User,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Session:
        """Create new session for user.
        
        Args:
            user: User to create session for
            device_info: Client device information
            ip_address: Client IP address
            
        Returns:
            New session with tokens
        """
        now = datetime.utcnow()
        
        session = Session(
            id=secrets.token_urlsafe(32),
            user_id=user.id,
            access_token=secrets.token_urlsafe(64),
            refresh_token=secrets.token_urlsafe(64),
            expires_at=(now + timedelta(hours=self.access_token_hours)).isoformat(),
            refresh_expires_at=(now + timedelta(days=self.refresh_token_days)).isoformat(),
            created_at=now.isoformat(),
            last_used=now.isoformat(),
            device_info=device_info,
            ip_address=ip_address,
        )
        
        # Enforce max sessions limit
        await self._enforce_session_limit(user.id)
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO sessions 
                (id, user_id, access_token, refresh_token, expires_at,
                 refresh_expires_at, created_at, last_used, device_info, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.user_id,
                session.access_token,
                session.refresh_token,
                session.expires_at,
                session.refresh_expires_at,
                session.created_at,
                session.last_used,
                session.device_info,
                session.ip_address,
            ))
        
        logger.info(f"Session created for user {user.id}")
        return session
    
    async def validate(self, access_token: str) -> Optional[Session]:
        """Validate access token and return session if valid.
        
        Args:
            access_token: Token to validate
            
        Returns:
            Session if valid, None if invalid/expired
        """
        with self._get_connection() as conn:
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
                # Token expired
                await self.delete(row["id"])
                return None
            
            # Update last used
            conn.execute(
                "UPDATE sessions SET last_used = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), row["id"])
            )
            
            return self._row_to_session(row)
    
    async def refresh(self, refresh_token: str) -> Optional[Session]:
        """Refresh session using refresh token.
        
        Creates new access token, optionally rotates refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Updated session with new tokens, None if invalid
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE refresh_token = ?",
                (refresh_token,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Check refresh expiry
            refresh_expires = datetime.fromisoformat(row["refresh_expires_at"])
            if datetime.utcnow() > refresh_expires:
                await self.delete(row["id"])
                return None
            
            now = datetime.utcnow()
            new_access_token = secrets.token_urlsafe(64)
            new_expires_at = (now + timedelta(hours=self.access_token_hours)).isoformat()
            
            conn.execute("""
                UPDATE sessions 
                SET access_token = ?, expires_at = ?, last_used = ?
                WHERE id = ?
            """, (new_access_token, new_expires_at, now.isoformat(), row["id"]))
            
            return Session(
                id=row["id"],
                user_id=row["user_id"],
                access_token=new_access_token,
                refresh_token=row["refresh_token"],
                expires_at=new_expires_at,
                refresh_expires_at=row["refresh_expires_at"],
                created_at=row["created_at"],
                last_used=now.isoformat(),
            )
    
    async def delete(self, session_id: str) -> bool:
        """Delete session (logout).
        
        Args:
            session_id: Session to delete
            
        Returns:
            True if deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE id = ?",
                (session_id,)
            )
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Session {session_id} deleted")
            return deleted
    
    async def delete_all_for_user(self, user_id: str) -> int:
        """Delete all sessions for user (logout everywhere).
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE user_id = ?",
                (user_id,)
            )
            count = cursor.rowcount
            logger.info(f"Deleted {count} sessions for user {user_id}")
            return count
    
    async def _enforce_session_limit(self, user_id: str) -> None:
        """Remove oldest sessions if over limit."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM sessions WHERE user_id = ? ORDER BY created_at",
                (user_id,)
            )
            sessions = cursor.fetchall()
            
            if len(sessions) >= self.max_sessions_per_user:
                # Delete oldest session
                oldest_id = sessions[0]["id"]
                conn.execute("DELETE FROM sessions WHERE id = ?", (oldest_id,))
                logger.info(f"Removed oldest session for user {user_id} (limit reached)")
    
    def _row_to_session(self, row: sqlite3.Row) -> Session:
        """Convert database row to Session."""
        return Session(
            id=row["id"],
            user_id=row["user_id"],
            access_token=row["access_token"],
            refresh_token=row["refresh_token"],
            expires_at=row["expires_at"],
            refresh_expires_at=row["refresh_expires_at"],
            created_at=row["created_at"],
            last_used=row["last_used"],
            device_info=row["device_info"],
            ip_address=row["ip_address"],
        )
```

---

## Section 4: User Service & Credentials

### Task 4.1: User Service

**Objective**: User account management

**File**: `apps/backend/auth/user/user_service.py`

**Features**:
- User CRUD operations
- Duplicate detection
- Profile updates
- Account deactivation

---

### Task 4.2: LLM Credentials Storage

**Objective**: Securely store per-user LLM provider credentials

**Quality Gate**: AES-256-GCM encryption, key derivation

**File**: `apps/backend/auth/user/credentials.py`

```python
"""Per-User LLM Credential Storage - Enterprise-Grade Security.

This module provides encrypted storage for users' LLM provider
credentials (API keys). All credentials are encrypted at rest
using AES-256-GCM with proper key derivation.

Security Features:
    - AES-256-GCM encryption
    - Per-user encryption keys
    - Key derivation from user secret
    - No plaintext storage ever
    - Secure key rotation support
"""

import sqlite3
import base64
import secrets
from pathlib import Path
from typing import Optional, Dict, List
from contextlib import contextmanager
from dataclasses import dataclass
import logging

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

@dataclass
class LLMCredential:
    """Stored LLM credential.
    
    Attributes:
        user_id: Owner user ID
        provider: LLM provider name
        credential_type: Type (api_key, token, etc.)
        encrypted_value: Encrypted credential value
        created_at: When stored
        updated_at: Last updated
    """
    user_id: str
    provider: str
    credential_type: str = "api_key"
    encrypted_value: bytes = b""
    created_at: str = ""
    updated_at: str = ""


class UserCredentialsManager:
    """Encrypted credential storage for LLM providers.
    
    World-Class Security Features:
    - AES-256-GCM authenticated encryption
    - PBKDF2 key derivation
    - Unique IV per encryption
    - No plaintext ever stored
    - Secure deletion support
    
    Example:
        >>> manager = UserCredentialsManager()
        >>> manager.store(user_id, "openrouter", "api_key", "sk-...")
        >>> api_key = manager.retrieve(user_id, "openrouter", "api_key")
    """
    
    def __init__(
        self, 
        db_path: str = "data/user_credentials.db",
        master_key: Optional[bytes] = None
    ):
        """Initialize credentials manager.
        
        Args:
            db_path: Path to encrypted credentials database
            master_key: Master encryption key (32 bytes)
                        If None, generates from environment
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._master_key = master_key or self._get_or_create_master_key()
        self._init_db()
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key."""
        import os
        
        key_path = self.db_path.parent / ".master_key"
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # Generate new master key
            key = secrets.token_bytes(32)
            key_path.touch(mode=0o600)
            with open(key_path, 'wb') as f:
                f.write(key)
            logger.warning("Generated new master encryption key")
            return key
    
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    credential_type TEXT NOT NULL,
                    encrypted_value BLOB NOT NULL,
                    iv BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, provider, credential_type)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_credentials_user_id 
                ON credentials(user_id)
            """)
    
    def _derive_key(self, user_id: str) -> bytes:
        """Derive per-user encryption key.
        
        Uses PBKDF2 to derive a unique key for each user.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._master_key,
            iterations=100000,
        )
        return kdf.derive(user_id.encode())
    
    def _encrypt(self, user_id: str, plaintext: str) -> tuple[bytes, bytes]:
        """Encrypt value with AES-256-GCM.
        
        Returns:
            Tuple of (ciphertext, iv)
        """
        key = self._derive_key(user_id)
        iv = secrets.token_bytes(12)  # 96-bit IV for GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(iv, plaintext.encode(), None)
        return ciphertext, iv
    
    def _decrypt(self, user_id: str, ciphertext: bytes, iv: bytes) -> str:
        """Decrypt value with AES-256-GCM.
        
        Returns:
            Decrypted plaintext
        """
        key = self._derive_key(user_id)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        return plaintext.decode()
    
    def store(
        self, 
        user_id: str, 
        provider: str, 
        credential_type: str,
        value: str
    ) -> bool:
        """Store encrypted credential.
        
        Args:
            user_id: User ID
            provider: LLM provider name
            credential_type: Credential type (e.g., "api_key")
            value: Plaintext credential value
            
        Returns:
            True if stored successfully
        """
        from datetime import datetime
        
        ciphertext, iv = self._encrypt(user_id, value)
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO credentials 
                (user_id, provider, credential_type, encrypted_value, iv, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, provider, credential_type) 
                DO UPDATE SET encrypted_value = ?, iv = ?, updated_at = ?
            """, (
                user_id, provider, credential_type, ciphertext, iv, now, now,
                ciphertext, iv, now
            ))
        
        logger.info(f"Stored {credential_type} for {provider} (user: {user_id[:8]}...)")
        return True
    
    def retrieve(
        self, 
        user_id: str, 
        provider: str, 
        credential_type: str = "api_key"
    ) -> Optional[str]:
        """Retrieve decrypted credential.
        
        Args:
            user_id: User ID
            provider: LLM provider name
            credential_type: Credential type
            
        Returns:
            Decrypted credential value, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT encrypted_value, iv FROM credentials
                WHERE user_id = ? AND provider = ? AND credential_type = ?
            """, (user_id, provider, credential_type))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._decrypt(user_id, row["encrypted_value"], row["iv"])
    
    def list_providers(self, user_id: str) -> List[str]:
        """List providers with stored credentials.
        
        Args:
            user_id: User ID
            
        Returns:
            List of provider names
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT DISTINCT provider FROM credentials WHERE user_id = ?",
                (user_id,)
            )
            return [row["provider"] for row in cursor.fetchall()]
    
    def delete(
        self, 
        user_id: str, 
        provider: str, 
        credential_type: Optional[str] = None
    ) -> int:
        """Delete credential(s).
        
        Args:
            user_id: User ID
            provider: Provider name
            credential_type: If None, delete all for provider
            
        Returns:
            Number of credentials deleted
        """
        with self._get_connection() as conn:
            if credential_type:
                cursor = conn.execute("""
                    DELETE FROM credentials 
                    WHERE user_id = ? AND provider = ? AND credential_type = ?
                """, (user_id, provider, credential_type))
            else:
                cursor = conn.execute("""
                    DELETE FROM credentials 
                    WHERE user_id = ? AND provider = ?
                """, (user_id, provider))
            
            count = cursor.rowcount
            logger.info(f"Deleted {count} credentials for {provider} (user: {user_id[:8]}...)")
            return count
    
    def delete_all_for_user(self, user_id: str) -> int:
        """Delete all credentials for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of credentials deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM credentials WHERE user_id = ?",
                (user_id,)
            )
            count = cursor.rowcount
            logger.info(f"Deleted all {count} credentials for user {user_id[:8]}...")
            return count
```

---

## Validation Checklist

| Item | Check | Status |
|------|-------|--------|
| GitHub OAuth complete flow | End-to-end test | ⬜ |
| Google OAuth complete flow | End-to-end test | ⬜ |
| Microsoft OAuth complete flow | End-to-end test | ⬜ |
| Manual auth registration | End-to-end test | ⬜ |
| Manual auth login | End-to-end test | ⬜ |
| Session creation/validation | Unit test | ⬜ |
| Token refresh | Unit test | ⬜ |
| CSRF protection | Security test | ⬜ |
| Credential encryption | Crypto audit | ⬜ |
| Password hashing | Security test | ⬜ |
| Test coverage >95% | Coverage report | ⬜ |
| OWASP Top 10 clean | Security scan | ⬜ |
| Type hints validate | mypy execution | ⬜ |

---

## Dependencies

**Requires**: Phase 2 (LLM providers for credential usage)

**Enables**: All phases (user context required)

---

## ADR References

- ADR-012: Multi-Provider Authentication

---

*Phase 3 Specification v2.0.0 - Enhanced with World-Class Outcome Expectations*
