"""Security models for threat detection and access control.

World-Class Standards:
- Comprehensive threat taxonomy with 6 threat types
- Fine-grained permission model with role-based access
- Provider-aware credential management for all 8 LLM providers
- Immutable audit events with integrity checksums
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from enum import Enum
import hashlib
import uuid


class ThreatType(Enum):
    """Comprehensive threat classification taxonomy."""
    SECRET_EXPOSED = "secret_exposed"
    PROMPT_INJECTION = "prompt_injection"
    CODE_INJECTION = "code_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CREDENTIAL_THEFT = "credential_theft"
    DATA_EXFILTRATION = "data_exfiltration"
    DATA_LEAK = "data_leak"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class Severity(Enum):
    """Threat severity levels aligned with CVSS."""
    LOW = "low"          # CVSS 0.1-3.9
    MEDIUM = "medium"    # CVSS 4.0-6.9
    HIGH = "high"        # CVSS 7.0-8.9
    CRITICAL = "critical"  # CVSS 9.0-10.0

    @classmethod
    def from_score(cls, score: float) -> "Severity":
        """Convert CVSS score to severity level."""
        if score >= 9.0:
            return cls.CRITICAL
        elif score >= 7.0:
            return cls.HIGH
        elif score >= 4.0:
            return cls.MEDIUM
        return cls.LOW


class AuditAction(Enum):
    """Auditable security actions for complete event tracking."""
    # Authentication events
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    
    # Credential events
    CREDENTIAL_ADDED = "credential_added"
    CREDENTIAL_ACCESSED = "credential_accessed"
    CREDENTIAL_REMOVED = "credential_removed"
    CREDENTIAL_ROTATED = "credential_rotated"
    
    # Agent events
    AGENT_CREATED = "agent_created"
    AGENT_DELETED = "agent_deleted"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    
    # Task events
    TASK_CREATED = "task_created"
    TASK_EXECUTED = "task_executed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # Permission events
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    PERMISSION_CHANGED = "permission_changed"
    PERMISSION_DENIED = "permission_denied"
    
    # Security events
    SECRET_DETECTED = "secret_detected"
    INJECTION_BLOCKED = "injection_blocked"
    THREAT_DETECTED = "threat_detected"
    
    # Provider events
    LLM_PROVIDER_CHANGED = "llm_provider_changed"
    LLM_CALL_MADE = "llm_call_made"
    LLM_CALL_FAILED = "llm_call_failed"


class PermissionScope(Enum):
    """Permission scope levels for RBAC."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class SecurityFinding:
    """Security scan finding with comprehensive metadata.
    
    Represents a detected security issue with full context
    for investigation and remediation.
    """
    id: str
    threat_type: ThreatType
    severity: Severity
    message: str
    source: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration
    cvss_score: Optional[float] = None
    provider: Optional[str] = None  # LLM provider if applicable
    detected_at: str = ""
    false_positive: bool = False
    acknowledged: bool = False
    resolved: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.detected_at:
            self.detected_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score,
            "provider": self.provider,
            "detected_at": self.detected_at,
            "false_positive": self.false_positive,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
        }


@dataclass
class AuditEvent:
    """Immutable audit log entry with integrity verification.
    
    Each event includes a checksum for tamper detection.
    Events are append-only and cannot be modified.
    """
    id: str
    action: AuditAction
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    resource: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    provider: Optional[str] = None  # LLM provider if applicable
    timestamp: str = ""
    success: bool = True
    error_message: Optional[str] = None
    checksum: Optional[str] = None
    previous_checksum: Optional[str] = None  # Chain integrity
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.checksum:
            self.checksum = self._compute_checksum()
    
    def _compute_checksum(self) -> str:
        """Compute SHA-256 checksum for integrity verification."""
        content = f"{self.id}{self.action.value}{self.user_id}{self.agent_id}"
        content += f"{self.resource}{self.timestamp}{self.success}"
        if self.previous_checksum:
            content += self.previous_checksum
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify event has not been tampered with."""
        return self.checksum == self._compute_checksum()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "action": self.action.value,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "resource": self.resource,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "provider": self.provider,
            "timestamp": self.timestamp,
            "success": self.success,
            "error_message": self.error_message,
            "checksum": self.checksum,
            "previous_checksum": self.previous_checksum,
        }


@dataclass
class Role:
    """User/agent role with fine-grained permissions.
    
    Supports hierarchical permissions with inheritance
    and provider-specific access control.
    """
    id: str
    name: str
    description: str = ""
    permissions: Set[str] = field(default_factory=set)
    is_system: bool = False
    parent_role: Optional[str] = None  # For inheritance
    provider_access: Set[str] = field(default_factory=set)  # LLM providers
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission."""
        if "*" in self.permissions or "*:*" in self.permissions:
            return True
        if permission in self.permissions:
            return True
        # Check wildcard patterns
        parts = permission.split(":")
        if len(parts) == 2:
            resource, action = parts
            if f"{resource}:*" in self.permissions:
                return True
            if f"*:{action}" in self.permissions:
                return True
        return False
    
    def can_access_provider(self, provider: str) -> bool:
        """Check if role can access an LLM provider."""
        if "*" in self.provider_access:
            return True
        return provider in self.provider_access
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": list(self.permissions),
            "is_system": self.is_system,
            "parent_role": self.parent_role,
            "provider_access": list(self.provider_access),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class EncryptedCredential:
    """Encrypted credential with full metadata.
    
    Stores encrypted API keys and secrets for LLM providers
    with rotation tracking and expiration support.
    """
    id: str
    provider: str
    credential_name: str
    ciphertext: bytes
    nonce: bytes
    auth_tag: bytes
    user_id: str
    created_at: str = ""
    rotated_at: Optional[str] = None
    expires_at: Optional[str] = None
    version: int = 1
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
    
    def is_expired(self) -> bool:
        """Check if credential has expired."""
        if not self.expires_at:
            return False
        expiry = datetime.fromisoformat(self.expires_at)
        return datetime.utcnow() > expiry


@dataclass
class ValidationResult:
    """Result of input/output validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_value: Optional[str] = None
    findings: List[SecurityFinding] = field(default_factory=list)
    
    def __bool__(self) -> bool:
        return self.valid


# LLM Provider Constants - All 8 providers with equal support
SUPPORTED_PROVIDERS = [
    "copilot",
    "openrouter", 
    "ollama",
    "lmstudio",
    "gemini",
    "openai",
    "anthropic",
    "azure",
]

# Provider credential requirements
PROVIDER_CREDENTIALS = {
    "copilot": ["GITHUB_TOKEN"],
    "openrouter": ["OPENROUTER_API_KEY"],
    "ollama": [],  # Local, no API key
    "lmstudio": [],  # Local, no API key
    "gemini": ["GOOGLE_API_KEY", "GOOGLE_PROJECT_ID"],
    "openai": ["OPENAI_API_KEY", "OPENAI_ORG_ID"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "azure": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_TENANT_ID"],
}
