"""Security Infrastructure Module for Auto-Claude APEXDEV.

Phase 6 Implementation - Enterprise-Grade Security

This module provides comprehensive security infrastructure including:
- Secrets scanning for all 8 LLM providers
- Prompt injection defense with multi-layer protection
- AES-256-GCM encryption for credential storage
- RBAC with provider-aware permissions
- Immutable audit logging with integrity verification
- Input/output validation with PII redaction

Supported LLM Providers (Equal Treatment):
- copilot (GitHub Copilot)
- openrouter
- ollama (local)
- lmstudio (local)
- gemini (Google)
- openai
- anthropic
- azure (Azure OpenAI)

Usage:
    from apps.backend.security import (
        SecretsScanner,
        PromptInjectionGuard,
        CredentialVault,
        RoleManager,
        AuditLogger,
        InputValidator,
        OutputValidator,
    )
    
    # Scan for exposed secrets
    scanner = SecretsScanner()
    findings = scanner.scan_text(code_content)
    
    # Protect against prompt injection
    guard = PromptInjectionGuard()
    result = guard.check(user_input)
    
    # Store credentials securely
    vault = CredentialVault()
    await vault.initialize()
    await vault.store_credential("openai", {"api_key": "sk-..."})
    
    # Manage roles and permissions
    manager = RoleManager()
    await manager.assign_role("user123", "developer", "admin")
    
    # Log security events
    logger = AuditLogger()
    await logger.log_event(
        action=AuditAction.LOGIN_SUCCESS,
        actor="user@example.com",
        resource="auth_service",
    )

Architecture:
    security/
    ├── __init__.py          # This file - main exports
    ├── models.py            # Core security domain models
    ├── config.py            # Security configuration
    ├── scanner/             # Threat detection scanners
    │   ├── secrets_scanner.py
    │   ├── prompt_injection.py
    │   ├── code_scanner.py
    │   ├── pattern_registry.py
    │   └── sanitizer.py
    ├── encryption/          # Credential encryption
    │   ├── credential_vault.py
    │   ├── key_manager.py
    │   └── crypto_utils.py
    ├── audit/               # Audit logging
    │   ├── audit_logger.py
    │   ├── event_types.py
    │   ├── integrity_checker.py
    │   └── audit_storage.py
    ├── rbac/                # Role-based access control
    │   ├── role_manager.py
    │   ├── permission_checker.py
    │   ├── policy_enforcer.py
    │   └── role_definitions.py
    └── validation/          # Input/output validation
        ├── input_validator.py
        ├── output_validator.py
        ├── schema_validator.py
        └── threat_detector.py

Compliance:
    - OWASP Top 10 for LLM Applications
    - OWASP ASVS Level 2
    - FIPS 197 (AES-256-GCM)
    - OWASP 2023 PBKDF2 recommendations (600K iterations)

Version: 3.2.0
Phase: 6 - Security Infrastructure
"""

# Core models
from .models import (
    ThreatType,
    Severity,
    AuditAction,
    PermissionScope,
    SecurityFinding,
    AuditEvent,
    Role,
    EncryptedCredential,
    ValidationResult,
    SUPPORTED_PROVIDERS,
    PROVIDER_CREDENTIALS,
)

# Configuration
from .config import (
    SecurityConfig,
    ScannerConfig,
    EncryptionConfig,
    AuditConfig,
    RBACConfig,
    ValidationConfig,
)

# Scanner module
from .scanner import (
    SecretsScanner,
    PromptInjectionGuard,
    PromptInjectionScanner,
    CodeScanner,
    PatternRegistry,
    InputSanitizer,
)

# Encryption module
from .encryption import (
    CredentialVault,
    KeyManager,
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    derive_key,
    generate_salt,
    secure_random_bytes,
)

# Audit module
from .audit import (
    AuditLogger,
    AuditEventType,
    SecurityEventType,
    AccessEventType,
    DataEventType,
    IntegrityChecker,
    AuditStorage,
    FileAuditStorage,
)

# RBAC module
from .rbac import (
    RoleManager,
    PermissionChecker,
    PolicyEnforcer,
    DefaultRoles,
    Permission,
    RoleDefinition,
    PROVIDER_PERMISSIONS,
)

# Validation module
from .validation import (
    InputValidator,
    OutputValidator,
    PIIRedactor,
    SchemaValidator,
    ThreatDetector,
)

__version__ = "3.2.0"
__phase__ = "6 - Security Infrastructure"

# Hooks
from .hooks import bash_security_hook, validate_command


# Parser
from .parser import extract_commands, split_command_segments, get_command_for_validation

# Profile
from .profile import get_security_profile, reset_profile_cache

# Validators
from .validator import (
    validate_pkill_command,
    validate_kill_command,
    validate_killall_command,
    validate_chmod_command,
    validate_rm_command,
    validate_init_script,
    validate_git_commit,
    validate_git_config,
    validate_git_command,
    validate_dropdb_command,
    validate_dropuser_command,
    validate_psql_command,
    validate_mysql_command,
    validate_mysqladmin_command,
    validate_mongosh_command,
    validate_redis_cli_command,
    VALIDATORS,
    get_validator,
    ValidationResult,
    ValidatorFunction,
)

__all__ = [
    "bash_security_hook",
    # Version info
    "__version__",
    "__phase__",
    
    # Core models
    "ThreatType",
    "Severity",
    "AuditAction",
    "PermissionScope",
    "SecurityFinding",
    "AuditEvent",
    "Role",
    "EncryptedCredential",
    "ValidationResult",
    "SUPPORTED_PROVIDERS",
    "PROVIDER_CREDENTIALS",
    
    # Configuration
    "SecurityConfig",
    "ScannerConfig",
    "EncryptionConfig",
    "AuditConfig",
    "RBACConfig",
    "ValidationConfig",
    
    # Scanners
    "SecretsScanner",
    "PromptInjectionGuard",
    "PromptInjectionScanner",
    "CodeScanner",
    "PatternRegistry",
    "InputSanitizer",
    
    # Encryption
    "CredentialVault",
    "KeyManager",
    "encrypt_aes_gcm",
    "decrypt_aes_gcm",
    "derive_key",
    "generate_salt",
    "secure_random_bytes",
    
    # Audit
    "AuditLogger",
    "AuditEventType",
    "SecurityEventType",
    "AccessEventType",
    "DataEventType",
    "IntegrityChecker",
    "AuditStorage",
    "FileAuditStorage",
    
    # RBAC
    "RoleManager",
    "PermissionChecker",
    "PolicyEnforcer",
    "DefaultRoles",
    "Permission",
    "RoleDefinition",
    "PROVIDER_PERMISSIONS",
    
    # Validation
    "InputValidator",
    "OutputValidator",
    "PIIRedactor",
    "SchemaValidator",
    "ThreatDetector",
]
