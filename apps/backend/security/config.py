"""Security configuration for Phase 6 infrastructure.

World-Class Standards:
- Comprehensive security settings
- Provider-aware configuration
- OWASP compliance settings
- Performance threshold tuning
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScannerConfig:
    """Configuration for security scanners."""

    # Performance thresholds
    max_scan_time_ms: int = 500  # Max time per file
    max_file_size_kb: int = 10240  # 10MB max
    batch_size: int = 100  # Files per batch

    # Detection settings
    enable_secrets_scan: bool = True
    enable_prompt_injection_scan: bool = True
    enable_code_scan: bool = True

    # Excluded patterns
    excluded_paths: set[str] = field(
        default_factory=lambda: {
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".mypy_cache",
            ".pytest_cache",
            "dist",
            "build",
        }
    )
    excluded_extensions: set[str] = field(
        default_factory=lambda: {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
        }
    )


@dataclass
class EncryptionConfig:
    """Configuration for credential encryption."""

    # Algorithm settings (AES-256-GCM)
    algorithm: str = "AES-256-GCM"
    key_length: int = 32  # 256 bits
    nonce_length: int = 12  # 96 bits for GCM
    tag_length: int = 16  # 128 bits

    # Key derivation
    kdf_algorithm: str = "PBKDF2-SHA256"
    kdf_iterations: int = 600000  # OWASP recommendation 2024
    salt_length: int = 32

    # Key rotation
    key_rotation_days: int = 90
    warn_before_expiry_days: int = 14

    # Storage
    vault_path: str = ".apexdev/credentials"
    backup_enabled: bool = True
    backup_count: int = 3


@dataclass
class AuditConfig:
    """Configuration for audit logging."""

    # Storage
    log_path: str = ".apexdev/audit/audit.log"
    max_log_size_mb: int = 100
    rotation_count: int = 10

    # Retention
    retention_days: int = 365
    archive_enabled: bool = True
    archive_path: str = ".apexdev/audit/archive"

    # Performance
    buffer_size: int = 1000  # Events before flush
    flush_interval_seconds: int = 60

    # Integrity
    enable_checksums: bool = True
    enable_chain_verification: bool = True

    # Database
    use_sqlite: bool = True
    sqlite_path: str = ".apexdev/audit/audit.db"


@dataclass
class RBACConfig:
    """Configuration for role-based access control."""

    # Cache settings
    permission_cache_ttl_seconds: int = 300
    role_cache_ttl_seconds: int = 600

    # Default roles
    default_user_role: str = "user"
    default_agent_role: str = "agent"

    # Provider permissions prefix
    provider_permission_prefix: str = "llm"

    # Enforcement
    strict_mode: bool = True  # Deny unknown permissions
    log_denials: bool = True


@dataclass
class ValidationConfig:
    """Configuration for input/output validation."""

    # Input limits
    max_input_length: int = 1_000_000  # 1MB
    max_prompt_length: int = 100_000  # 100KB

    # Sanitization
    sanitize_html: bool = True
    sanitize_sql: bool = True
    sanitize_shell: bool = True

    # PII detection
    redact_pii: bool = True
    pii_patterns: list[str] = field(
        default_factory=lambda: [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
            r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",  # SSN
            r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",  # Credit card
        ]
    )


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    # Global limits
    requests_per_minute: int = 60
    requests_per_hour: int = 1000

    # Per-provider limits
    provider_limits: dict[str, int] = field(
        default_factory=lambda: {
            "copilot": 100,
            "openrouter": 60,
            "ollama": 1000,  # Local, higher limit
            "lmstudio": 1000,  # Local, higher limit
            "gemini": 60,
            "openai": 60,
            "anthropic": 40,
            "azure": 60,
        }
    )

    # Burst settings
    burst_multiplier: float = 1.5
    cooldown_seconds: int = 60


@dataclass
class SecurityConfig:
    """Master security configuration.

    Aggregates all security subsystem configurations
    with sensible enterprise-grade defaults.
    """

    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    rbac: RBACConfig = field(default_factory=RBACConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    # Global settings
    debug_mode: bool = False
    strict_mode: bool = True  # Fail on any security issue

    # Supported LLM providers (all 8)
    supported_providers: list[str] = field(
        default_factory=lambda: [
            "copilot",
            "openrouter",
            "ollama",
            "lmstudio",
            "gemini",
            "openai",
            "anthropic",
            "azure",
        ]
    )

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Load configuration from environment variables."""
        config = cls()

        # Override from environment
        if os.getenv("SECURITY_DEBUG"):
            config.debug_mode = os.getenv("SECURITY_DEBUG", "").lower() == "true"
        if os.getenv("SECURITY_STRICT_MODE"):
            config.strict_mode = (
                os.getenv("SECURITY_STRICT_MODE", "").lower() != "false"
            )

        # Audit path
        if audit_path := os.getenv("SECURITY_AUDIT_PATH"):
            config.audit.log_path = audit_path
            config.audit.sqlite_path = str(Path(audit_path).parent / "audit.db")

        # Vault path
        if vault_path := os.getenv("SECURITY_VAULT_PATH"):
            config.encryption.vault_path = vault_path

        # Rate limits
        if rpm := os.getenv("SECURITY_RATE_LIMIT_RPM"):
            config.rate_limit.requests_per_minute = int(rpm)

        return config

    def validate(self) -> list[str]:
        """Validate configuration and return any errors."""
        errors = []

        if self.encryption.key_length not in [16, 24, 32]:
            errors.append("Invalid AES key length. Must be 16, 24, or 32 bytes.")

        if self.encryption.kdf_iterations < 100000:
            errors.append("KDF iterations below OWASP minimum of 100,000.")

        if self.audit.retention_days < 30:
            errors.append("Audit retention below recommended 30 days.")

        if self.rate_limit.requests_per_minute < 1:
            errors.append("Rate limit must be at least 1 request per minute.")

        return errors


# Default configuration instance
default_config = SecurityConfig()
