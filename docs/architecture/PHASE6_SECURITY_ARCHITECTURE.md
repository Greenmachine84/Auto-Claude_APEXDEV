# Phase 6: Security Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 6 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026
> Reference: `docs/specs/phase-06-security.md`

---

## Overview

Phase 6 implements comprehensive security infrastructure including secrets scanning, prompt injection defense, credential encryption, audit logging, and RBAC enforcement. All security components are **LLM-Agnostic** and support credential storage for all 8 LLM providers.

---

## Quality Standards

| Standard | Target | Verification |
|----------|--------|-------------|
| OWASP Top 10 | 100% Coverage | Security audit |
| SOC 2 Type II | Ready | Compliance review |
| Zero Critical Vulns | ✅ | Penetration test |
| AES-256-GCM Encryption | ✅ | Crypto audit |

---

## Directory Structure

```
apps/
└── backend/
    └── security/
        ├── __init__.py                    # Security module exports
        ├── models.py                      # Security models (ThreatType, Severity, AuditAction)
        ├── config.py                      # Security configuration
        │
        ├── scanner/
        │   ├── __init__.py                # Scanner exports
        │   ├── secrets_scanner.py         # Multi-provider secrets detection
        │   ├── prompt_injection.py        # Prompt injection defense
        │   ├── code_scanner.py            # Code vulnerability scanning
        │   ├── pattern_registry.py        # Detection pattern registry
        │   └── sanitizer.py               # Input sanitization
        │
        ├── encryption/
        │   ├── __init__.py                # Encryption exports
        │   ├── credential_vault.py        # Multi-provider credential vault
        │   ├── key_manager.py             # Key management and rotation
        │   └── crypto_utils.py            # AES-256-GCM utilities
        │
        ├── audit/
        │   ├── __init__.py                # Audit exports
        │   ├── audit_logger.py            # Immutable audit logging
        │   ├── event_types.py             # Audit event definitions
        │   ├── integrity_checker.py       # Log integrity verification
        │   └── audit_storage.py           # Audit log persistence
        │
        ├── rbac/
        │   ├── __init__.py                # RBAC exports
        │   ├── role_manager.py            # Role management
        │   ├── permission_checker.py      # Access control validation
        │   ├── policy_enforcer.py         # Permission enforcement
        │   └── role_definitions.py        # Default role definitions
        │
        └── validation/
            ├── __init__.py                # Validation exports
            ├── input_validator.py         # Input validation
            ├── output_validator.py        # Output validation (PII redaction)
            ├── schema_validator.py        # Schema validation
            └── threat_detector.py         # Threat pattern detection
```

---

## File Specifications

### 1. Core Security Module (`security/`)

#### `models.py`
**Purpose**: Security domain models and enums
**Key Components**:
```python
class ThreatType(Enum):
    SECRET_EXPOSED = "secret_exposed"
    PROMPT_INJECTION = "prompt_injection"
    CODE_INJECTION = "code_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CREDENTIAL_THEFT = "credential_theft"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditAction(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREDENTIAL_ADDED = "credential_added"
    CREDENTIAL_ACCESSED = "credential_accessed"
    CREDENTIAL_REMOVED = "credential_removed"
    LLM_PROVIDER_CHANGED = "llm_provider_changed"
    SECRET_DETECTED = "secret_detected"
    # ... additional actions

@dataclass
class SecurityFinding:
    id: str
    threat_type: ThreatType
    severity: Severity
    message: str
    source: str
    line_number: Optional[int]
    evidence: Optional[str]
    remediation: Optional[str]

@dataclass
class AuditEvent:
    id: str
    action: AuditAction
    user_id: Optional[str]
    agent_id: Optional[str]
    resource: Optional[str]
    details: Dict[str, Any]
    timestamp: str
    checksum: Optional[str]  # Integrity verification
```

#### `config.py`
**Purpose**: Security configuration and thresholds
**Key Components**:
- Scanning thresholds
- Rate limit defaults
- Encryption settings
- Audit retention policies

---

### 2. Scanner Module (`security/scanner/`)

#### `secrets_scanner.py`
**Purpose**: Detect exposed secrets including all 8 LLM provider credentials
**Key Components**:
```python
class SecretsScanner:
    """Multi-provider secrets detection."""
    
    # Patterns for all 8 LLM providers
    PATTERNS = {
        "github_token": {"pattern": r"gh[pousr]_[A-Za-z0-9_]{36,}", "provider": "copilot"},
        "openrouter_key": {"pattern": r"sk-or-[A-Za-z0-9]{48,}", "provider": "openrouter"},
        "openai_key": {"pattern": r"sk-[A-Za-z0-9]{48,}", "provider": "openai"},
        "anthropic_key": {"pattern": r"sk-ant-[A-Za-z0-9-]{90,}", "provider": "anthropic"},
        "google_api_key": {"pattern": r"AIza[0-9A-Za-z-_]{35}", "provider": "gemini"},
        "azure_key": {"pattern": r"(?i)azure.{0,20}['\"](key)", "provider": "azure"},
    }
    
    def scan_text(self, text: str, source: str) -> List[SecurityFinding]
    def scan_file(self, file_path: Path) -> List[SecurityFinding]
    def scan_directory(self, directory: Path) -> List[SecurityFinding]
```

**Methods**:
- `scan_text()` - Scan text content for secrets
- `scan_file()` - Scan single file
- `scan_directory()` - Recursive directory scan
- `_redact()` - Redact sensitive content from evidence

#### `prompt_injection.py`
**Purpose**: Multi-layer prompt injection defense
**Key Components**:
```python
class PromptInjectionGuard:
    """Defense against prompt injection attacks."""
    
    DETECTION_PATTERNS = [
        r"ignore (all )?previous instructions",
        r"you are now",
        r"system prompt",
        r"\]\]\]",  # Delimiter escape attempts
    ]
    
    def check(self, input_text: str) -> ValidationResult
    def sanitize(self, input_text: str) -> str
    def wrap_user_input(self, input_text: str) -> str
    def validate_output(self, output: str) -> ValidationResult
```

#### `code_scanner.py`
**Purpose**: Static code analysis for vulnerabilities
**Key Components**:
- SQL injection detection
- XSS vulnerability detection
- Path traversal detection
- Command injection detection

#### `pattern_registry.py`
**Purpose**: Centralized registry of detection patterns
**Key Components**:
- Pattern registration and lookup
- Pattern versioning
- Custom pattern support

#### `sanitizer.py`
**Purpose**: Input sanitization utilities
**Key Components**:
- HTML sanitization
- SQL escaping
- Shell command sanitization

---

### 3. Encryption Module (`security/encryption/`)

#### `credential_vault.py`
**Purpose**: Secure credential storage for all 8 LLM providers
**Key Components**:
```python
class CredentialVault:
    """
    Secure vault for multi-provider credentials.
    
    Supports all 8 providers with isolated storage:
    - copilot, openrouter, ollama, lmstudio
    - gemini, openai, anthropic, azure
    """
    
    PROVIDER_CREDENTIALS = {
        "copilot": ["GITHUB_TOKEN"],
        "openrouter": ["OPENROUTER_API_KEY"],
        "ollama": [],  # Local, no API key
        "lmstudio": [],  # Local, no API key
        "gemini": ["GOOGLE_API_KEY", "GOOGLE_PROJECT_ID"],
        "openai": ["OPENAI_API_KEY", "OPENAI_ORG_ID"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "azure": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
    }
    
    def store_credential(self, user_id, provider, name, value) -> bool
    def get_credential(self, user_id, provider, name) -> Optional[str]
    def rotate_credential(self, user_id, provider, name, new_value) -> bool
    def delete_credential(self, user_id, provider, name) -> bool
    def list_credentials(self, user_id, provider) -> List[str]
```

#### `key_manager.py`
**Purpose**: Encryption key management and rotation
**Key Components**:
```python
class KeyManager:
    """Key management with rotation support."""
    
    def generate_key(self) -> bytes
    def rotate_key(self) -> Tuple[bytes, bytes]  # old, new
    def derive_key(self, password: str, salt: bytes) -> bytes
    def get_current_key(self) -> bytes
```

#### `crypto_utils.py`
**Purpose**: AES-256-GCM encryption utilities
**Key Components**:
```python
def encrypt(plaintext: str, key: bytes) -> Tuple[bytes, bytes, bytes]  # ciphertext, nonce, tag
def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes) -> str
def generate_nonce() -> bytes
def verify_tag(ciphertext: bytes, tag: bytes) -> bool
```

---

### 4. Audit Module (`security/audit/`)

#### `audit_logger.py`
**Purpose**: Immutable, tamper-proof audit logging
**Key Components**:
```python
class AuditLogger:
    """Append-only audit logging with integrity verification."""
    
    def log(self, event: AuditEvent) -> str  # Returns event ID
    def log_auth(self, action, user_id, provider, success) -> str
    def log_credential_access(self, user_id, provider, credential_name) -> str
    def log_llm_call(self, user_id, provider, model, tokens) -> str
    def log_security_finding(self, finding: SecurityFinding) -> str
```

#### `event_types.py`
**Purpose**: Comprehensive audit event type definitions
**Key Components**:
- Authentication events
- Credential events
- LLM provider events
- Agent execution events
- Security events

#### `integrity_checker.py`
**Purpose**: Verify audit log integrity
**Key Components**:
```python
class IntegrityChecker:
    def verify_log(self, log_file: Path) -> bool
    def verify_event(self, event: AuditEvent) -> bool
    def detect_tampering(self, log_file: Path) -> List[int]  # Tampered line numbers
```

#### `audit_storage.py`
**Purpose**: Audit log persistence and retrieval
**Key Components**:
- SQLite storage backend
- Log rotation
- Retention policy enforcement
- Query interface

---

### 5. RBAC Module (`security/rbac/`)

#### `role_manager.py`
**Purpose**: Role and permission management
**Key Components**:
```python
class RoleManager:
    def create_role(self, role: Role) -> str
    def update_role(self, role_id: str, updates: Dict) -> Role
    def delete_role(self, role_id: str) -> bool
    def assign_role(self, user_id: str, role_id: str) -> bool
    def revoke_role(self, user_id: str, role_id: str) -> bool
    def get_user_roles(self, user_id: str) -> List[Role]
```

#### `permission_checker.py`
**Purpose**: Access control validation
**Key Components**:
```python
class PermissionChecker:
    def check(self, user_id: str, permission: str, resource: str) -> bool
    def check_agent_capability(self, agent_id: str, capability: str) -> bool
    def check_provider_access(self, user_id: str, provider: str) -> bool
```

#### `policy_enforcer.py`
**Purpose**: Permission enforcement at execution time
**Key Components**:
- Decorator-based enforcement
- Middleware integration
- Denial logging

#### `role_definitions.py`
**Purpose**: Default role and permission definitions
**Key Components**:
```python
DEFAULT_ROLES = {
    "admin": {"permissions": ["*"]},
    "developer": {"permissions": ["read:*", "write:code", "execute:agent"]},
    "viewer": {"permissions": ["read:*"]},
}

PROVIDER_PERMISSIONS = {
    "use_copilot", "use_openrouter", "use_ollama", "use_lmstudio",
    "use_gemini", "use_openai", "use_anthropic", "use_azure",
}
```

---

### 6. Validation Module (`security/validation/`)

#### `input_validator.py`
**Purpose**: Input validation and sanitization
**Key Components**:
```python
class InputValidator:
    def validate(self, input_data: Any, schema: Dict) -> ValidationResult
    def sanitize_html(self, html: str) -> str
    def sanitize_sql(self, sql: str) -> str
    def check_length(self, text: str, max_length: int) -> bool
```

#### `output_validator.py`
**Purpose**: Output validation and PII redaction
**Key Components**:
```python
class OutputValidator:
    def validate(self, output: Any, schema: Dict) -> ValidationResult
    def redact_pii(self, text: str) -> str
    def redact_secrets(self, text: str) -> str
    def check_format(self, output: Any, expected_format: str) -> bool
```

#### `schema_validator.py`
**Purpose**: JSON schema validation
**Key Components**:
- JSON Schema validation
- Pydantic model validation
- Custom schema definitions

#### `threat_detector.py`
**Purpose**: Real-time threat pattern detection
**Key Components**:
```python
class ThreatDetector:
    def detect(self, content: str) -> List[ThreatIndicator]
    def classify_threat(self, indicator: ThreatIndicator) -> Severity
    def recommend_action(self, threat: ThreatIndicator) -> str
```

---

## LLM-Agnostic Security

### Multi-Provider Credential Security

All 8 LLM providers have equal security treatment:

| Provider | Credentials Stored | Encryption |
|----------|-------------------|------------|
| copilot | GITHUB_TOKEN | AES-256-GCM |
| openrouter | OPENROUTER_API_KEY | AES-256-GCM |
| ollama | (local, none) | N/A |
| lmstudio | (local, none) | N/A |
| gemini | GOOGLE_API_KEY, PROJECT_ID | AES-256-GCM |
| openai | OPENAI_API_KEY, ORG_ID | AES-256-GCM |
| anthropic | ANTHROPIC_API_KEY | AES-256-GCM |
| azure | API_KEY, ENDPOINT, TENANT_ID | AES-256-GCM |

### Provider-Specific Secret Detection

Each provider has unique secret patterns for detection:
- GitHub tokens: `gh[pousr]_*`
- OpenRouter keys: `sk-or-*`
- OpenAI keys: `sk-*` (but not `sk-ant-*`)
- Anthropic keys: `sk-ant-*`
- Google keys: `AIza*`
- Azure keys: Context-based detection

---

## Integration Points

### With Authentication (Phase 3)
- RBAC integrates with user sessions
- Permission checks on all authenticated requests

### With LLM Providers (Phase 2)
- Credential vault provides secure API key access
- Secrets scanner prevents key exposure

### With Audit/Governance (Phase 9)
- Audit logs feed into compliance reporting
- RBAC policies enforced by governance engine

### With Agents (Phase 7)
- Agent capabilities validated by RBAC
- Agent outputs scanned for security

---

## Performance Targets

| Operation | Target | Threshold |
|-----------|--------|----------|
| Secrets scan per file | <100ms | 500ms |
| Prompt injection check | <5ms | 20ms |
| Encryption/decryption | <1ms | 5ms |
| Audit log write | <10ms | 50ms |
| RBAC check | <1ms | 5ms |

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `security/` (core) | 3 | Core security module |
| `security/scanner/` | 6 | Secret/vulnerability scanning |
| `security/encryption/` | 4 | Credential encryption |
| `security/audit/` | 5 | Audit logging |
| `security/rbac/` | 5 | Access control |
| `security/validation/` | 5 | Input/output validation |
| **Total** | **28** | Phase 6 files |

---

## Test Requirements

| Test Category | Coverage Target |
|---------------|----------------|
| Secrets scanner | 95% |
| Prompt injection | 95% |
| Credential vault | 100% |
| Audit logging | 90% |
| RBAC | 95% |

---

## Next Steps

→ Phase 7: Enterprise Agents Architecture

---

*Phase 6 Architecture complete. 28 files specified for security module.*
