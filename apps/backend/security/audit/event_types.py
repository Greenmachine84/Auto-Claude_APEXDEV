"""Audit event type definitions.

World-Class Standards:
- Comprehensive event categorization
- Security-focused event types
- Severity mapping
- Action mapping
"""
from enum import Enum
from typing import Optional

from ..models import AuditAction, Severity


class AuditEventType(Enum):
    """Base audit event type enumeration."""
    
    # General events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIG_CHANGE = "config_change"
    ERROR = "error"
    
    def to_audit_action(self) -> AuditAction:
        """Convert to AuditAction."""
        mapping = {
            self.SYSTEM_START: AuditAction.SYSTEM_EVENT,
            self.SYSTEM_STOP: AuditAction.SYSTEM_EVENT,
            self.CONFIG_CHANGE: AuditAction.SETTINGS_UPDATED,
            self.ERROR: AuditAction.SYSTEM_EVENT,
        }
        return mapping.get(self, AuditAction.SYSTEM_EVENT)
    
    def default_severity(self) -> Severity:
        """Get default severity for this event type."""
        severity_map = {
            self.SYSTEM_START: Severity.LOW,
            self.SYSTEM_STOP: Severity.LOW,
            self.CONFIG_CHANGE: Severity.MEDIUM,
            self.ERROR: Severity.HIGH,
        }
        return severity_map.get(self, Severity.LOW)


class SecurityEventType(Enum):
    """Security-specific event types."""
    
    # Threat detection
    THREAT_DETECTED = "threat_detected"
    SECRET_EXPOSED = "secret_exposed"
    INJECTION_ATTEMPT = "injection_attempt"
    MALICIOUS_CODE = "malicious_code"
    
    # Scanning events
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    VULNERABILITY_FOUND = "vulnerability_found"
    
    # Input validation
    INPUT_BLOCKED = "input_blocked"
    OUTPUT_SANITIZED = "output_sanitized"
    PII_DETECTED = "pii_detected"
    
    # Key management
    KEY_CREATED = "key_created"
    KEY_ROTATED = "key_rotated"
    KEY_DELETED = "key_deleted"
    
    def to_audit_action(self) -> AuditAction:
        """Convert to AuditAction."""
        mapping = {
            self.THREAT_DETECTED: AuditAction.THREAT_DETECTED,
            self.SECRET_EXPOSED: AuditAction.SECRET_DETECTED,
            self.INJECTION_ATTEMPT: AuditAction.INJECTION_BLOCKED,
            self.MALICIOUS_CODE: AuditAction.MALICIOUS_CODE_BLOCKED,
            self.SCAN_STARTED: AuditAction.SCAN_STARTED,
            self.SCAN_COMPLETED: AuditAction.SCAN_COMPLETED,
            self.VULNERABILITY_FOUND: AuditAction.VULNERABILITY_DISCOVERED,
            self.INPUT_BLOCKED: AuditAction.INPUT_VALIDATED,
            self.OUTPUT_SANITIZED: AuditAction.OUTPUT_SANITIZED,
            self.PII_DETECTED: AuditAction.PII_REDACTED,
            self.KEY_CREATED: AuditAction.KEY_GENERATED,
            self.KEY_ROTATED: AuditAction.KEY_ROTATED,
            self.KEY_DELETED: AuditAction.KEY_DELETED,
        }
        return mapping.get(self, AuditAction.SYSTEM_EVENT)
    
    def default_severity(self) -> Severity:
        """Get default severity for this event type."""
        high_severity = {
            self.THREAT_DETECTED,
            self.SECRET_EXPOSED,
            self.INJECTION_ATTEMPT,
            self.MALICIOUS_CODE,
            self.VULNERABILITY_FOUND,
            self.PII_DETECTED,
        }
        
        if self in high_severity:
            return Severity.HIGH
        return Severity.MEDIUM


class AccessEventType(Enum):
    """Access control event types."""
    
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    
    # Authorization
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    
    # Provider access
    PROVIDER_ACCESS_GRANTED = "provider_access_granted"
    PROVIDER_ACCESS_DENIED = "provider_access_denied"
    
    def to_audit_action(self) -> AuditAction:
        """Convert to AuditAction."""
        mapping = {
            self.LOGIN_SUCCESS: AuditAction.LOGIN_SUCCESS,
            self.LOGIN_FAILURE: AuditAction.LOGIN_FAILURE,
            self.LOGOUT: AuditAction.LOGOUT,
            self.SESSION_CREATED: AuditAction.SESSION_CREATED,
            self.SESSION_EXPIRED: AuditAction.SESSION_EXPIRED,
            self.ACCESS_GRANTED: AuditAction.ACCESS_GRANTED,
            self.ACCESS_DENIED: AuditAction.ACCESS_DENIED,
            self.PERMISSION_CHANGED: AuditAction.PERMISSION_CHANGED,
            self.ROLE_ASSIGNED: AuditAction.ROLE_ASSIGNED,
            self.ROLE_REVOKED: AuditAction.ROLE_REVOKED,
            self.PROVIDER_ACCESS_GRANTED: AuditAction.PROVIDER_ACCESS_GRANTED,
            self.PROVIDER_ACCESS_DENIED: AuditAction.PROVIDER_ACCESS_DENIED,
        }
        return mapping.get(self, AuditAction.SYSTEM_EVENT)
    
    def default_severity(self) -> Severity:
        """Get default severity for this event type."""
        high_severity = {
            self.LOGIN_FAILURE,
            self.ACCESS_DENIED,
            self.PROVIDER_ACCESS_DENIED,
        }
        
        medium_severity = {
            self.LOGIN_SUCCESS,
            self.PERMISSION_CHANGED,
            self.ROLE_ASSIGNED,
            self.ROLE_REVOKED,
        }
        
        if self in high_severity:
            return Severity.HIGH
        if self in medium_severity:
            return Severity.MEDIUM
        return Severity.LOW


class DataEventType(Enum):
    """Data operation event types."""
    
    # Credential operations
    CREDENTIAL_CREATED = "credential_created"
    CREDENTIAL_READ = "credential_read"
    CREDENTIAL_UPDATED = "credential_updated"
    CREDENTIAL_DELETED = "credential_deleted"
    CREDENTIAL_ROTATED = "credential_rotated"
    
    # Data operations
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    DATA_DELETED = "data_deleted"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    def to_audit_action(self) -> AuditAction:
        """Convert to AuditAction."""
        mapping = {
            self.CREDENTIAL_CREATED: AuditAction.CREDENTIAL_UPDATED,
            self.CREDENTIAL_READ: AuditAction.CREDENTIAL_RETRIEVED,
            self.CREDENTIAL_UPDATED: AuditAction.CREDENTIAL_UPDATED,
            self.CREDENTIAL_DELETED: AuditAction.CREDENTIAL_DELETED,
            self.CREDENTIAL_ROTATED: AuditAction.KEY_ROTATED,
            self.DATA_EXPORTED: AuditAction.DATA_EXPORTED,
            self.DATA_IMPORTED: AuditAction.DATA_IMPORTED,
            self.DATA_DELETED: AuditAction.DATA_DELETED,
            self.BACKUP_CREATED: AuditAction.BACKUP_CREATED,
            self.BACKUP_RESTORED: AuditAction.BACKUP_RESTORED,
        }
        return mapping.get(self, AuditAction.SYSTEM_EVENT)
    
    def default_severity(self) -> Severity:
        """Get default severity for this event type."""
        high_severity = {
            self.CREDENTIAL_CREATED,
            self.CREDENTIAL_UPDATED,
            self.CREDENTIAL_DELETED,
            self.CREDENTIAL_ROTATED,
            self.DATA_DELETED,
        }
        
        if self in high_severity:
            return Severity.HIGH
        return Severity.MEDIUM
