# Security API Reference

Complete API documentation for the Auto-Claude security system.

## Overview

The Security API provides interfaces for authentication, authorization,
input validation, secret management, and security scanning.

## Authentication

### API Key Authentication

```python
from apps.backend.security import ApiKeyAuth

auth = ApiKeyAuth(
    key_header="X-API-Key",
    validator=validate_api_key
)

@app.middleware
async def auth_middleware(request, call_next):
    if not await auth.authenticate(request):
        return Response(status_code=401)
    return await call_next(request)
```

### JWT Authentication

```python
from apps.backend.security import JWTAuth

jwt_auth = JWTAuth(
    secret=os.environ["JWT_SECRET"],
    algorithm="HS256",
    expiry_hours=24
)

# Generate token
token = jwt_auth.generate(user_id="user-123", roles=["admin"])

# Verify token
claims = jwt_auth.verify(token)
```

### OAuth2 Integration

```python
from apps.backend.security import OAuth2Provider

oauth = OAuth2Provider(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    authorize_url="https://provider.com/oauth/authorize",
    token_url="https://provider.com/oauth/token"
)

# Get authorization URL
auth_url = oauth.get_authorize_url(
    redirect_uri="https://app.com/callback",
    scope=["read", "write"]
)

# Exchange code for token
tokens = await oauth.exchange_code(code, redirect_uri)
```

## Authorization

### Role-Based Access Control

```python
from apps.backend.security import RBAC, Role, Permission

rbac = RBAC()

# Define roles
rbac.add_role(Role(
    name="developer",
    permissions=[
        Permission("code", "read"),
        Permission("code", "write"),
        Permission("tools", "execute")
    ]
))

rbac.add_role(Role(
    name="admin",
    permissions=[Permission("*", "*")],
    inherits=["developer"]
))

# Check permission
if rbac.can(user, "code", "write"):
    await perform_action()
```

### Permission Decorators

```python
from apps.backend.security import require_permission

@require_permission("code", "write")
async def modify_code(request):
    pass

@require_role("admin")
async def admin_action(request):
    pass
```

### Resource-Based Authorization

```python
from apps.backend.security import ResourceAuth

resource_auth = ResourceAuth()

@resource_auth.policy("project")
def project_policy(user, project, action):
    if action == "read":
        return project.is_public or user.id in project.members
    if action == "write":
        return user.id in project.editors
    return False

# Check access
if await resource_auth.can(user, project, "write"):
    await modify_project(project)
```

## Input Validation

### Schema Validation

```python
from apps.backend.security import validate_input, Schema

user_schema = Schema({
    "username": {"type": "string", "min_length": 3, "max_length": 50},
    "email": {"type": "string", "format": "email"},
    "age": {"type": "integer", "min": 13}
})

@validate_input(user_schema)
async def create_user(data: dict):
    pass
```

### Sanitization

```python
from apps.backend.security import sanitize

# Sanitize HTML
clean_html = sanitize.html(user_input)

# Sanitize for SQL (use parameterized queries instead)
safe_value = sanitize.sql_identifier(table_name)

# Sanitize file path
safe_path = sanitize.path(file_path, allowed_dirs=["/workspace"])

# Sanitize shell command
safe_cmd = sanitize.shell_arg(user_arg)
```

### Injection Prevention

```python
from apps.backend.security import (
    prevent_sql_injection,
    prevent_command_injection,
    prevent_path_traversal
)

# Path traversal check
if prevent_path_traversal(user_path, base_dir="/workspace"):
    # Safe to use path
    pass

# Command injection check
if prevent_command_injection(user_input):
    # Safe to include in command
    pass
```

## Secret Management

### SecretStore

```python
from apps.backend.security import SecretStore

secrets = SecretStore(
    backend="vault",
    config={"url": "https://vault.example.com"}
)

# Get secret
api_key = await secrets.get("api_keys/openai")

# Set secret
await secrets.set("api_keys/new_service", "secret-value")

# Rotate secret
await secrets.rotate("api_keys/openai")
```

### Environment Variable Loading

```python
from apps.backend.security import load_secrets

# Load from .env with validation
secrets = load_secrets(
    required=["DATABASE_URL", "API_KEY"],
    optional=["DEBUG_MODE"]
)
```

### Secret Masking

```python
from apps.backend.security import mask_secrets

# Mask secrets in logs
safe_log = mask_secrets(
    log_message,
    patterns=["api_key=", "password=", "token="]
)
logger.info(safe_log)
```

## Security Scanning

### Code Scanner

```python
from apps.backend.security import CodeScanner, ScanConfig

scanner = CodeScanner(
    config=ScanConfig(
        check_secrets=True,
        check_vulnerabilities=True,
        check_dependencies=True
    )
)

results = await scanner.scan(code, language="python")
for issue in results.issues:
    print(f"{issue.severity}: {issue.message}")
```

### Dependency Scanner

```python
from apps.backend.security import DependencyScanner

dep_scanner = DependencyScanner()

vulnerabilities = await dep_scanner.scan("requirements.txt")
for vuln in vulnerabilities:
    print(f"{vuln.package}: {vuln.cve} ({vuln.severity})")
```

### Secret Scanner

```python
from apps.backend.security import SecretScanner

secret_scanner = SecretScanner(
    patterns=SecretPatterns.default(),
    custom_patterns=[
        r"my_custom_token_[a-z0-9]{32}"
    ]
)

findings = secret_scanner.scan(content)
for finding in findings:
    print(f"Line {finding.line}: {finding.type}")
```

## Rate Limiting

### Rate Limiter

```python
from apps.backend.security import RateLimiter

limiter = RateLimiter(
    backend="redis",
    default_limit=100,
    default_window=60  # seconds
)

@limiter.limit("10/minute")
async def expensive_operation(request):
    pass

@limiter.limit("1000/hour", key_func=lambda r: r.user_id)
async def api_endpoint(request):
    pass
```

### Adaptive Rate Limiting

```python
from apps.backend.security import AdaptiveRateLimiter

adaptive = AdaptiveRateLimiter(
    base_limit=100,
    burst_limit=150,
    recovery_rate=10  # per second
)
```

## Audit Logging

### AuditLogger

```python
from apps.backend.security import AuditLogger

audit = AuditLogger(
    destination="elasticsearch",
    config={"hosts": ["localhost:9200"]}
)

await audit.log(
    action="user.login",
    actor=user_id,
    resource="session",
    outcome="success",
    metadata={"ip": request.ip}
)
```

### Audit Events

| Event | Description |
|-------|-------------|
| `auth.login` | User login attempt |
| `auth.logout` | User logout |
| `resource.create` | Resource created |
| `resource.update` | Resource modified |
| `resource.delete` | Resource deleted |
| `security.violation` | Security rule violated |

## Content Security

### Content Filter

```python
from apps.backend.security import ContentFilter

filter = ContentFilter(
    block_patterns=["malicious_pattern"],
    allow_html=False,
    max_length=10000
)

if filter.is_safe(user_content):
    await process_content(user_content)
```

### Output Sanitization

```python
from apps.backend.security import sanitize_output

# Prevent sensitive data leakage
safe_response = sanitize_output(
    response,
    redact_fields=["password", "ssn", "credit_card"]
)
```

## Encryption

### Data Encryption

```python
from apps.backend.security import Encryptor

encryptor = Encryptor(
    key=os.environ["ENCRYPTION_KEY"],
    algorithm="AES-256-GCM"
)

# Encrypt
encrypted = encryptor.encrypt(sensitive_data)

# Decrypt
decrypted = encryptor.decrypt(encrypted)
```

### Field-Level Encryption

```python
from apps.backend.security import EncryptedField

class User(Model):
    email = StringField()
    ssn = EncryptedField()  # Automatically encrypted/decrypted
```

## Best Practices

1. **Never trust input** - Validate and sanitize everything
2. **Principle of least privilege** - Minimal permissions
3. **Defense in depth** - Multiple security layers
4. **Secure by default** - Opt-in to reduced security
5. **Audit everything** - Log security events
6. **Keep secrets secret** - Use secret managers

## See Also

- [Security Overview](../security/security-overview.md)
- [Authentication Guide](../guides/authentication.md)
- [Deployment Security](../guides/deployment.md#security)
