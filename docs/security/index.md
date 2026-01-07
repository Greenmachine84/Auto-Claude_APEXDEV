# Security Documentation Index

Security documentation for Auto-Claude.

## Overview

This section provides comprehensive security documentation including
architecture, threat analysis, and best practices.

## Documents

### Core Security

- [Security Overview](security-overview.md) - Complete security architecture
- [Threat Model](threat-model.md) - Threat analysis and mitigations

### Implementation

- [Security API Reference](../api/security-api.md) - Security API documentation
- [Authentication Guide](../guides/authentication.md) - Auth implementation
- [Configuration Security](../guides/configuration.md#security-configuration) - Secure configuration

## Quick Reference

### Security Checklist

- [ ] API keys stored in environment variables
- [ ] JWT secrets are strong and rotated
- [ ] Rate limiting enabled
- [ ] Sandboxing configured
- [ ] Audit logging enabled
- [ ] TLS for all connections
- [ ] Dependencies scanned for vulnerabilities
- [ ] Code scanned for secrets

### Common Security Tasks

| Task | Documentation |
|------|---------------|
| Configure auth | [Security Overview](security-overview.md#authentication) |
| Set up sandboxing | [Security Overview](security-overview.md#sandboxing) |
| Enable audit logging | [Security Overview](security-overview.md#audit-logging) |
| Rotate secrets | [Security Overview](security-overview.md#secret-management) |

## Reporting Security Issues

For security vulnerabilities, please email security@example.com.

Do not open public issues for security problems.
