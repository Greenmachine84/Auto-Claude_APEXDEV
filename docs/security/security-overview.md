# Security Overview

Comprehensive security documentation for Auto-Claude.

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   AuthN     │  │   AuthZ     │  │   Input Validation  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Sandbox    │  │ Rate Limit  │  │   Secret Mgmt       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Audit     │  │  Scanning   │  │   Encryption        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Authentication

### Supported Methods

| Method | Use Case | Configuration |
|--------|----------|---------------|
| API Key | Service-to-service | `X-API-Key` header |
| JWT | User sessions | Bearer token |
| OAuth2 | SSO integration | Provider config |

### JWT Configuration

```yaml
security:
  auth:
    jwt:
      secret: ${JWT_SECRET}
      algorithm: HS256
      expiry_hours: 24
      refresh_enabled: true
      refresh_expiry_days: 7
```

### API Key Management

```python
from apps.backend.security import ApiKeyManager

manager = ApiKeyManager()

# Create key with permissions
key = await manager.create(
    name="my-service",
    permissions=["agent.execute", "memory.read"],
    expires_days=90
)

# Validate key
is_valid = await manager.validate(key.key_string)
```

## Authorization

### Role-Based Access Control (RBAC)

```yaml
security:
  rbac:
    roles:
      viewer:
        permissions:
          - read:*
      developer:
        permissions:
          - read:*
          - execute:agents
          - write:memory
      admin:
        permissions:
          - "*"
```

### Permission Model

| Resource | Actions | Description |
|----------|---------|-------------|
| `agents` | read, execute, configure | Agent operations |
| `memory` | read, write, delete | Memory access |
| `tools` | read, execute | Tool execution |
| `config` | read, write | Configuration |
| `audit` | read | Audit logs |

### Resource-Level Authorization

```python
from apps.backend.security import authorize

@authorize(resource="project", action="write")
async def modify_project(request, project_id):
    # Authorization checked automatically
    pass
```

## Input Validation

### Schema Validation

All API inputs are validated against JSON schemas:

```python
from apps.backend.security import validate_input

@validate_input({
    "type": "object",
    "properties": {
        "task": {"type": "string", "maxLength": 10000},
        "agent": {"type": "string", "pattern": "^[a-z_]+$"}
    },
    "required": ["task", "agent"]
})
async def execute_task(data: dict):
    pass
```

### Sanitization

```python
from apps.backend.security import sanitize

# Sanitize HTML to prevent XSS
safe_html = sanitize.html(user_input)

# Sanitize for shell commands
safe_arg = sanitize.shell_arg(user_input)

# Validate file paths
safe_path = sanitize.path(user_path, base_dir="/workspace")
```

### Injection Prevention

| Attack Type | Prevention |
|-------------|------------|
| SQL Injection | Parameterized queries |
| Command Injection | Input validation, allowlists |
| Path Traversal | Path canonicalization |
| XSS | Output encoding |
| Prompt Injection | Input filtering, guardrails |

## Sandboxing

### Tool Execution Sandbox

```yaml
security:
  sandbox:
    enabled: true
    isolation: process  # process, container, vm
    paths:
      allowed:
        - /workspace
        - /tmp/agent-output
      blocked:
        - /etc
        - /var
        - ~/.ssh
    network:
      allowed_hosts:
        - api.github.com
        - api.anthropic.com
      blocked_ports:
        - 22
        - 3306
    resources:
      max_memory_mb: 512
      max_cpu_seconds: 30
      max_file_size_mb: 10
```

### Container Isolation

```yaml
security:
  sandbox:
    isolation: container
    container:
      image: autoclaude/sandbox:latest
      read_only_root: true
      drop_capabilities:
        - NET_RAW
        - SYS_ADMIN
      seccomp_profile: default
```

## Rate Limiting

### Configuration

```yaml
security:
  rate_limiting:
    enabled: true
    backend: redis
    default:
      requests: 100
      window_seconds: 60
    endpoints:
      /api/agents/execute:
        requests: 10
        window_seconds: 60
      /api/memory/search:
        requests: 50
        window_seconds: 60
```

### Adaptive Rate Limiting

```python
from apps.backend.security import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter(
    base_limit=100,
    burst_limit=150,
    recovery_rate=10
)
```

## Secret Management

### Secret Storage

```yaml
security:
  secrets:
    backend: vault  # env, file, vault
    vault:
      url: https://vault.example.com
      auth_method: token
      mount_path: secret/autoclaude
```

### Secret Rotation

```python
from apps.backend.security import SecretManager

manager = SecretManager()

# Rotate API key
await manager.rotate("api_keys/openai")

# Get current secret
secret = await manager.get("api_keys/openai")
```

### Environment Variable Security

```bash
# Never commit .env files
# Use .env.example for templates

# Load secrets from environment
ANTHROPIC_API_KEY=${VAULT_ANTHROPIC_KEY}
DATABASE_URL=${VAULT_DATABASE_URL}
```

## Security Scanning

### Code Scanning

```yaml
security:
  scanning:
    code:
      enabled: true
      on: [commit, pr]
      checks:
        - secrets
        - vulnerabilities
        - code_quality
```

### Dependency Scanning

```yaml
security:
  scanning:
    dependencies:
      enabled: true
      schedule: daily
      fail_on:
        - critical
        - high
```

### Secret Scanning

```python
from apps.backend.security import SecretScanner

scanner = SecretScanner()
findings = scanner.scan(code_content)

for finding in findings:
    print(f"Secret found: {finding.type} at line {finding.line}")
```

## Audit Logging

### Configuration

```yaml
security:
  audit:
    enabled: true
    destination: elasticsearch
    events:
      - auth.login
      - auth.logout
      - agent.execute
      - tool.execute
      - config.change
    retention_days: 90
```

### Audit Events

```python
from apps.backend.security import audit_log

await audit_log(
    event="agent.execute",
    actor=user_id,
    resource=f"agent:{agent_id}",
    action="execute",
    outcome="success",
    metadata={"task_id": task_id}
)
```

## Encryption

### Data at Rest

```yaml
security:
  encryption:
    at_rest:
      enabled: true
      algorithm: AES-256-GCM
      key_source: kms  # kms, vault, env
```

### Data in Transit

```yaml
security:
  encryption:
    in_transit:
      tls:
        enabled: true
        min_version: TLS1.2
        certificates:
          cert_file: /etc/ssl/certs/server.crt
          key_file: /etc/ssl/private/server.key
```

### Field-Level Encryption

```python
from apps.backend.security import encrypt_field

# Encrypt sensitive data
encrypted = encrypt_field(ssn, key=encryption_key)

# Decrypt when needed
decrypted = decrypt_field(encrypted, key=encryption_key)
```

## Security Best Practices

### Development

1. **Never commit secrets** - Use environment variables
2. **Validate all input** - Trust nothing from users
3. **Use parameterized queries** - Prevent SQL injection
4. **Sanitize output** - Prevent XSS
5. **Apply least privilege** - Minimal permissions

### Operations

1. **Enable TLS** - Encrypt all traffic
2. **Rotate secrets regularly** - Automate rotation
3. **Monitor audit logs** - Detect anomalies
4. **Keep dependencies updated** - Patch vulnerabilities
5. **Regular security reviews** - Periodic assessments

### Agent Security

1. **Sandbox all execution** - Isolate agent actions
2. **Limit tool access** - Only necessary tools
3. **Validate agent output** - Check before acting
4. **Log all actions** - Full audit trail
5. **Set resource limits** - Prevent abuse

## Incident Response

### Detection

- Monitor audit logs for anomalies
- Set up alerts for security events
- Regular security scanning

### Response

1. **Contain** - Isolate affected systems
2. **Investigate** - Analyze audit logs
3. **Remediate** - Fix vulnerabilities
4. **Recover** - Restore normal operation
5. **Learn** - Update procedures

## Compliance

### Data Protection

- GDPR compliance features
- Data retention policies
- User consent management
- Data export/deletion

### Security Standards

- OWASP Top 10 mitigation
- CIS benchmarks
- SOC 2 controls

## See Also

- [Threat Model](threat-model.md)
- [Security API Reference](../api/security-api.md)
- [Configuration Guide](../guides/configuration.md)
