# Phase 6: Security

> **Duration**: Week 11-12 | **Priority**: 🟢 HIGH
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| Secrets detection | Pre-commit scanning | 100% |
| Prompt injection defense | Input sanitization | ✅ |
| Credential encryption | AES-256 at rest | ✅ |
| Audit logging | All auth events | ✅ |
| RBAC enforcement | Role-based access | ✅ |

### Deliverables

1. `apps/backend/security/scanner/secrets_scanner.py`
2. `apps/backend/security/scanner/prompt_injection.py`
3. `apps/backend/security/encryption/credential_vault.py`
4. `apps/backend/security/audit/audit_logger.py`
5. `apps/backend/security/rbac/role_manager.py`
6. `apps/backend/security/rbac/permission_checker.py`
7. Unit tests for all modules

---

## Section 1: Security Architecture

### Task 1.1: Directory Structure

```
apps/backend/security/
├── __init__.py
├── models.py
├── scanner/
│   ├── __init__.py
│   ├── secrets_scanner.py
│   ├── prompt_injection.py
│   └── code_scanner.py
├── encryption/
│   ├── __init__.py
│   ├── credential_vault.py
│   └── key_manager.py
├── audit/
│   ├── __init__.py
│   ├── audit_logger.py
│   └── event_types.py
└── rbac/
    ├── __init__.py
    ├── role_manager.py
    └── permission_checker.py
```

---

### Task 1.2: Security Models

**File**: `apps/backend/security/models.py`

```python
"""Security models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from enum import Enum

class ThreatType(Enum):
    SECRET_EXPOSED = "secret_exposed"
    PROMPT_INJECTION = "prompt_injection"
    CODE_INJECTION = "code_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditAction(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    CREDENTIAL_ADDED = "credential_added"
    CREDENTIAL_REMOVED = "credential_removed"
    AGENT_CREATED = "agent_created"
    AGENT_DELETED = "agent_deleted"
    TASK_EXECUTED = "task_executed"
    PERMISSION_CHANGED = "permission_changed"
    SECRET_DETECTED = "secret_detected"

@dataclass
class SecurityFinding:
    """Security scan finding."""
    id: str
    threat_type: ThreatType
    severity: Severity
    message: str
    source: str  # file path, input field, etc.
    line_number: Optional[int] = None
    evidence: Optional[str] = None  # Redacted snippet
    remediation: Optional[str] = None
    detected_at: str = ""
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.utcnow().isoformat()

@dataclass
class AuditEvent:
    """Audit log entry."""
    id: str
    action: AuditAction
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    resource: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: str = ""
    success: bool = True
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class Role:
    """User/agent role."""
    id: str
    name: str
    description: str = ""
    permissions: Set[str] = field(default_factory=set)
    is_system: bool = False  # Built-in role

@dataclass 
class Permission:
    """Permission definition."""
    id: str
    resource: str  # e.g., "agent", "memory", "credential"
    action: str    # e.g., "read", "write", "delete", "execute"
    
    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"

# Built-in roles
DEFAULT_ROLES = [
    Role(
        id="admin",
        name="Administrator",
        description="Full system access",
        permissions={"*:*"},
        is_system=True,
    ),
    Role(
        id="developer",
        name="Developer",
        description="Agent creation and management",
        permissions={
            "agent:read", "agent:write", "agent:execute",
            "memory:read", "memory:write",
            "credential:read", "credential:write",
        },
        is_system=True,
    ),
    Role(
        id="viewer",
        name="Viewer",
        description="Read-only access",
        permissions={
            "agent:read",
            "memory:read",
        },
        is_system=True,
    ),
]
```

---

## Section 2: Secrets Scanner

### Task 2.1: Secrets Scanner

**File**: `apps/backend/security/scanner/secrets_scanner.py`

```python
"""Secrets detection scanner."""
import re
from typing import List, Optional, Dict
from pathlib import Path
import uuid
from ..models import SecurityFinding, ThreatType, Severity

class SecretsScanner:
    """Detects exposed secrets in code and text."""
    
    # Pattern definitions with severity
    PATTERNS: Dict[str, Dict] = {
        "aws_access_key": {
            "pattern": r"AKIA[0-9A-Z]{16}",
            "severity": Severity.CRITICAL,
            "message": "AWS Access Key ID detected",
        },
        "aws_secret_key": {
            "pattern": r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]",
            "severity": Severity.CRITICAL,
            "message": "AWS Secret Key detected",
        },
        "github_token": {
            "pattern": r"gh[pousr]_[A-Za-z0-9_]{36,}",
            "severity": Severity.CRITICAL,
            "message": "GitHub Token detected",
        },
        "openai_key": {
            "pattern": r"sk-[A-Za-z0-9]{48,}",
            "severity": Severity.CRITICAL,
            "message": "OpenAI API Key detected",
        },
        "anthropic_key": {
            "pattern": r"sk-ant-[A-Za-z0-9-]{90,}",
            "severity": Severity.CRITICAL,
            "message": "Anthropic API Key detected",
        },
        "google_api_key": {
            "pattern": r"AIza[0-9A-Za-z-_]{35}",
            "severity": Severity.HIGH,
            "message": "Google API Key detected",
        },
        "azure_key": {
            "pattern": r"(?i)azure.{0,20}['\"][A-Za-z0-9+/]{43}=['\"]?",
            "severity": Severity.CRITICAL,
            "message": "Azure Key detected",
        },
        "private_key": {
            "pattern": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
            "severity": Severity.CRITICAL,
            "message": "Private key detected",
        },
        "jwt_token": {
            "pattern": r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
            "severity": Severity.MEDIUM,
            "message": "JWT Token detected",
        },
        "generic_secret": {
            "pattern": r"(?i)(password|secret|api_key|apikey|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
            "severity": Severity.MEDIUM,
            "message": "Potential secret in variable assignment",
        },
    }
    
    def __init__(self):
        self._compiled_patterns = {
            name: re.compile(info["pattern"])
            for name, info in self.PATTERNS.items()
        }
    
    def scan_text(self, text: str, source: str = "input") -> List[SecurityFinding]:
        """Scan text for secrets."""
        findings = []
        lines = text.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            for name, pattern in self._compiled_patterns.items():
                matches = pattern.findall(line)
                for match in matches:
                    info = self.PATTERNS[name]
                    findings.append(SecurityFinding(
                        id=str(uuid.uuid4()),
                        threat_type=ThreatType.SECRET_EXPOSED,
                        severity=info["severity"],
                        message=info["message"],
                        source=source,
                        line_number=line_num,
                        evidence=self._redact(match if isinstance(match, str) else match[0]),
                        remediation=f"Remove {name} from source and rotate credential",
                    ))
        
        return findings
    
    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan file for secrets."""
        if not file_path.exists():
            return []
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return self.scan_text(content, str(file_path))
        except Exception:
            return []
    
    def scan_directory(
        self, 
        directory: Path,
        extensions: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> List[SecurityFinding]:
        """Scan directory recursively."""
        findings = []
        exclude = exclude or [".git", "node_modules", "__pycache__", ".venv"]
        extensions = extensions or [
            ".py", ".js", ".ts", ".json", ".yaml", ".yml", 
            ".env", ".conf", ".config", ".md", ".txt"
        ]
        
        for path in directory.rglob("*"):
            # Skip excluded directories
            if any(exc in path.parts for exc in exclude):
                continue
            
            # Skip non-matching extensions
            if path.is_file() and path.suffix in extensions:
                findings.extend(self.scan_file(path))
        
        return findings
    
    def _redact(self, secret: str, visible: int = 4) -> str:
        """Redact secret showing only first/last chars."""
        if len(secret) <= visible * 2:
            return "*" * len(secret)
        return secret[:visible] + "*" * (len(secret) - visible * 2) + secret[-visible:]
```

---

### Task 2.2: Prompt Injection Defense

**File**: `apps/backend/security/scanner/prompt_injection.py`

```python
"""Prompt injection detection and defense."""
import re
from typing import List, Tuple, Optional
import uuid
from ..models import SecurityFinding, ThreatType, Severity

class PromptInjectionDefense:
    """Detects and mitigates prompt injection attacks."""
    
    # Known injection patterns
    INJECTION_PATTERNS = [
        # Direct instruction override
        (r"(?i)ignore (previous|all|above|prior) (instructions?|prompts?|rules?)", Severity.HIGH),
        (r"(?i)disregard (your|the|all) (instructions?|programming|rules?)", Severity.HIGH),
        (r"(?i)forget (everything|what|your)", Severity.MEDIUM),
        
        # Role manipulation
        (r"(?i)you are (now|actually) (a|an|the)", Severity.MEDIUM),
        (r"(?i)pretend (you are|to be|you're)", Severity.MEDIUM),
        (r"(?i)act as (if|a|an|the)", Severity.LOW),
        
        # System prompt extraction
        (r"(?i)(reveal|show|display|print|output) (your|the|system) (prompt|instructions?)", Severity.HIGH),
        (r"(?i)what (is|are) your (instructions?|system prompt|rules?)", Severity.MEDIUM),
        
        # Delimiter attacks
        (r"(?i)\[\s*system\s*\]", Severity.HIGH),
        (r"(?i)\[\s*INST\s*\]", Severity.HIGH),
        (r"###\s*(system|instruction|human|assistant)", Severity.MEDIUM),
        
        # Code execution attempts
        (r"(?i)execute (this|the following) (code|command)", Severity.HIGH),
        (r"(?i)run (this|the following) (script|code)", Severity.HIGH),
        
        # Data exfiltration
        (r"(?i)(send|transmit|exfiltrate) (to|data|information)", Severity.HIGH),
    ]
    
    def __init__(self):
        self._compiled = [
            (re.compile(pattern), severity)
            for pattern, severity in self.INJECTION_PATTERNS
        ]
    
    def analyze(self, text: str) -> Tuple[bool, List[SecurityFinding]]:
        """Analyze text for injection attempts.
        
        Returns:
            Tuple of (is_suspicious, findings)
        """
        findings = []
        
        for pattern, severity in self._compiled:
            matches = pattern.findall(text)
            if matches:
                findings.append(SecurityFinding(
                    id=str(uuid.uuid4()),
                    threat_type=ThreatType.PROMPT_INJECTION,
                    severity=severity,
                    message="Potential prompt injection detected",
                    source="user_input",
                    evidence=matches[0] if matches else None,
                    remediation="Review input and consider blocking",
                ))
        
        is_suspicious = len(findings) > 0
        return is_suspicious, findings
    
    def sanitize(self, text: str) -> str:
        """Sanitize input by escaping dangerous patterns."""
        # Escape common delimiters used in attacks
        sanitized = text
        
        # Escape markdown-style headers that could be delimiters
        sanitized = re.sub(r"^###", r"\\###", sanitized, flags=re.MULTILINE)
        
        # Escape bracket commands
        sanitized = re.sub(r"\[(system|INST|instruction)\]", r"[\1]", sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def wrap_user_input(self, user_input: str) -> str:
        """Wrap user input with clear boundaries."""
        return f"""<user_input>
{self.sanitize(user_input)}
</user_input>"""
```

---

## Section 3: Audit Logging

### Task 3.1: Audit Logger

**File**: `apps/backend/security/audit/audit_logger.py`

```python
"""Security audit logging."""
import sqlite3
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import uuid
from ..models import AuditEvent, AuditAction

class AuditLogger:
    """Logs security-relevant events."""
    
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    agent_id TEXT,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT NOT NULL,
                    success INTEGER NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user ON audit_log(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_action ON audit_log(action)")
    
    async def log(self, event: AuditEvent) -> str:
        """Log audit event."""
        if not event.id:
            event.id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_log
                (id, action, user_id, agent_id, resource, details,
                 ip_address, user_agent, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.action.value,
                event.user_id,
                event.agent_id,
                event.resource,
                json.dumps(event.details),
                event.ip_address,
                event.user_agent,
                event.timestamp,
                1 if event.success else 0,
            ))
        
        return event.id
    
    async def query(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit log."""
        conditions = ["1=1"]
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            conditions.append("action = ?")
            params.append(action.value)
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.isoformat())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.isoformat())
        
        params.append(limit)
        
        sql = f"""
            SELECT * FROM audit_log
            WHERE {' AND '.join(conditions)}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            return [
                AuditEvent(
                    id=row["id"],
                    action=AuditAction(row["action"]),
                    user_id=row["user_id"],
                    agent_id=row["agent_id"],
                    resource=row["resource"],
                    details=json.loads(row["details"] or "{}"),
                    ip_address=row["ip_address"],
                    user_agent=row["user_agent"],
                    timestamp=row["timestamp"],
                    success=bool(row["success"]),
                )
                for row in cursor.fetchall()
            ]
    
    async def get_failed_logins(
        self, 
        user_id: str, 
        window_minutes: int = 15
    ) -> int:
        """Count failed logins in time window (for rate limiting)."""
        start = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM audit_log
                WHERE user_id = ?
                AND action = ?
                AND timestamp >= ?
                AND success = 0
            """, (user_id, AuditAction.LOGIN_FAILED.value, start.isoformat()))
            
            return cursor.fetchone()[0]
```

---

## Section 4: RBAC

### Task 4.1: Role Manager

**File**: `apps/backend/security/rbac/role_manager.py`

```python
"""Role-based access control management."""
import sqlite3
import json
from typing import Optional, List, Set
from pathlib import Path
from ..models import Role, Permission, DEFAULT_ROLES

class RoleManager:
    """Manages roles and user-role assignments."""
    
    def __init__(self, db_path: str = "rbac.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    permissions TEXT NOT NULL,
                    is_system INTEGER NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id TEXT NOT NULL,
                    role_id TEXT NOT NULL,
                    granted_at TEXT,
                    granted_by TEXT,
                    PRIMARY KEY (user_id, role_id)
                )
            """)
            
            # Insert default roles
            for role in DEFAULT_ROLES:
                conn.execute("""
                    INSERT OR IGNORE INTO roles
                    (id, name, description, permissions, is_system)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    role.id,
                    role.name,
                    role.description,
                    json.dumps(list(role.permissions)),
                    1 if role.is_system else 0,
                ))
    
    async def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM roles WHERE id = ?", (role_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Role(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                permissions=set(json.loads(row["permissions"])),
                is_system=bool(row["is_system"]),
            )
    
    async def assign_role(
        self, 
        user_id: str, 
        role_id: str,
        granted_by: Optional[str] = None
    ) -> bool:
        """Assign role to user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_roles
                (user_id, role_id, granted_at, granted_by)
                VALUES (?, ?, datetime('now'), ?)
            """, (user_id, role_id, granted_by))
        return True
    
    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke role from user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM user_roles WHERE user_id = ? AND role_id = ?",
                (user_id, role_id)
            )
        return True
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT r.* FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ?
            """, (user_id,))
            
            return [
                Role(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"] or "",
                    permissions=set(json.loads(row["permissions"])),
                    is_system=bool(row["is_system"]),
                )
                for row in cursor.fetchall()
            ]
    
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user (union of all roles)."""
        roles = await self.get_user_roles(user_id)
        permissions: Set[str] = set()
        
        for role in roles:
            permissions.update(role.permissions)
        
        return permissions
```

---

### Task 4.2: Permission Checker

**File**: `apps/backend/security/rbac/permission_checker.py`

```python
"""Permission checking utility."""
from typing import Optional
from .role_manager import RoleManager

class PermissionChecker:
    """Checks user permissions."""
    
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager
    
    async def check(
        self, 
        user_id: str, 
        resource: str, 
        action: str
    ) -> bool:
        """Check if user has permission."""
        permissions = await self.role_manager.get_user_permissions(user_id)
        
        # Check for wildcard permission
        if "*:*" in permissions:
            return True
        
        # Check for resource wildcard
        if f"{resource}:*" in permissions:
            return True
        
        # Check for action wildcard
        if f"*:{action}" in permissions:
            return True
        
        # Check specific permission
        return f"{resource}:{action}" in permissions
    
    async def require(
        self, 
        user_id: str, 
        resource: str, 
        action: str
    ) -> None:
        """Require permission, raise if denied."""
        if not await self.check(user_id, resource, action):
            raise PermissionError(
                f"User {user_id} lacks {resource}:{action} permission"
            )
```

---

## Validation Checklist

- [ ] Secrets scanner detects all pattern types
- [ ] Prompt injection defense catches attacks
- [ ] Input sanitization works
- [ ] Audit events logged correctly
- [ ] Audit queries return correct results
- [ ] Default roles created on init
- [ ] Role assignment/revocation works
- [ ] Permission checking works with wildcards
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 3 (Authentication)

**Enables**: Phase 7 (Enterprise Agents), Phase 9 (Governance)

---

## ADR References

- ADR-010: Security Model Harmonization

---

*Phase 6 Specification v1.0.0*
