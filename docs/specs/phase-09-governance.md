# Phase 9: Governance

> **Duration**: Week 17-18 | **Priority**: 🟠 LOW
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| Policy engine works | Rule enforcement | ✅ |
| Approval workflows | Multi-step approvals | ✅ |
| Rate limiting | Per-user/agent limits | ✅ |
| Compliance logging | Audit trail | ✅ |
| Quota management | Resource limits | ✅ |

### Deliverables

1. `apps/backend/governance/policy/policy_engine.py`
2. `apps/backend/governance/policy/rules.py`
3. `apps/backend/governance/workflow/approval_workflow.py`
4. `apps/backend/governance/limits/rate_limiter.py`
5. `apps/backend/governance/limits/quota_manager.py`
6. `apps/backend/governance/compliance/compliance_logger.py`
7. Unit tests for all modules

---

## Section 1: Governance Architecture

### Task 1.1: Directory Structure

```
apps/backend/governance/
├── __init__.py
├── models.py
├── policy/
│   ├── __init__.py
│   ├── policy_engine.py
│   └── rules.py
├── workflow/
│   ├── __init__.py
│   └── approval_workflow.py
├── limits/
│   ├── __init__.py
│   ├── rate_limiter.py
│   └── quota_manager.py
└── compliance/
    ├── __init__.py
    └── compliance_logger.py
```

---

### Task 1.2: Governance Models

**File**: `apps/backend/governance/models.py`

```python
"""Governance models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG = "log"
    WARN = "warn"

class RuleOperator(Enum):
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    CONTAINS = "contains"
    MATCHES = "matches"  # regex
    IN = "in"
    NOT_IN = "not_in"

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class PolicyRule:
    """Single policy rule."""
    id: str
    name: str
    description: str = ""
    field: str = ""       # Field to check (e.g., "agent.provider")
    operator: RuleOperator = RuleOperator.EQUALS
    value: Any = None     # Value to compare
    action: PolicyAction = PolicyAction.ALLOW
    priority: int = 0     # Higher = evaluated first
    enabled: bool = True
    conditions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class Policy:
    """Collection of rules."""
    id: str
    name: str
    description: str = ""
    rules: List[PolicyRule] = field(default_factory=list)
    default_action: PolicyAction = PolicyAction.ALLOW
    enabled: bool = True
    applies_to: List[str] = field(default_factory=list)  # user_ids, role_ids

@dataclass
class PolicyEvaluation:
    """Result of policy evaluation."""
    policy_id: str
    action: PolicyAction
    matched_rule: Optional[str] = None
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ApprovalRequest:
    """Request requiring approval."""
    id: str
    request_type: str  # agent_creation, dangerous_action, etc.
    requester_id: str
    description: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    approvers: List[str] = field(default_factory=list)
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: str = ""
    expires_at: Optional[str] = None
    completed_at: Optional[str] = None

@dataclass
class RateLimit:
    """Rate limit configuration."""
    id: str
    target_type: str  # user, agent, global
    target_id: Optional[str] = None  # Specific user/agent or None for global
    resource: str = "*"  # What is being limited (requests, tokens, etc.)
    max_count: int = 100
    window_seconds: int = 60
    enabled: bool = True

@dataclass
class Quota:
    """Resource quota."""
    id: str
    user_id: str
    resource: str  # tokens, requests, cost, etc.
    limit: float
    period: str = "monthly"  # daily, weekly, monthly
    current_usage: float = 0.0
    reset_at: str = ""
```

---

## Section 2: Policy Engine

### Task 2.1: Policy Engine

**File**: `apps/backend/governance/policy/policy_engine.py`

```python
"""Policy evaluation engine."""
import re
from typing import Dict, Any, List, Optional
from ..models import (
    Policy, PolicyRule, PolicyEvaluation, PolicyAction, RuleOperator
)

class PolicyEngine:
    """Evaluates policies against contexts."""
    
    def __init__(self):
        self._policies: Dict[str, Policy] = {}
    
    def register(self, policy: Policy) -> None:
        """Register a policy."""
        self._policies[policy.id] = policy
    
    def unregister(self, policy_id: str) -> bool:
        """Unregister a policy."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False
    
    async def evaluate(
        self,
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        role_ids: Optional[List[str]] = None
    ) -> List[PolicyEvaluation]:
        """Evaluate all applicable policies."""
        evaluations = []
        
        for policy in self._policies.values():
            if not policy.enabled:
                continue
            
            # Check if policy applies to user/role
            if policy.applies_to:
                applies = False
                if user_id and user_id in policy.applies_to:
                    applies = True
                if role_ids:
                    for role in role_ids:
                        if role in policy.applies_to:
                            applies = True
                            break
                if not applies:
                    continue
            
            evaluation = await self._evaluate_policy(policy, context)
            evaluations.append(evaluation)
        
        return evaluations
    
    async def _evaluate_policy(
        self,
        policy: Policy,
        context: Dict[str, Any]
    ) -> PolicyEvaluation:
        """Evaluate a single policy."""
        # Sort rules by priority (descending)
        rules = sorted(
            [r for r in policy.rules if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in rules:
            if await self._evaluate_rule(rule, context):
                return PolicyEvaluation(
                    policy_id=policy.id,
                    action=rule.action,
                    matched_rule=rule.id,
                    reason=rule.description or f"Matched rule: {rule.name}",
                )
        
        # No rule matched, use default
        return PolicyEvaluation(
            policy_id=policy.id,
            action=policy.default_action,
            reason="No rules matched, using default action",
        )
    
    async def _evaluate_rule(
        self,
        rule: PolicyRule,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single rule against context."""
        # Get field value from context using dot notation
        actual = self._get_nested(context, rule.field)
        expected = rule.value
        
        if rule.operator == RuleOperator.EQUALS:
            return actual == expected
        elif rule.operator == RuleOperator.NOT_EQUALS:
            return actual != expected
        elif rule.operator == RuleOperator.GREATER_THAN:
            return actual > expected
        elif rule.operator == RuleOperator.LESS_THAN:
            return actual < expected
        elif rule.operator == RuleOperator.CONTAINS:
            return expected in actual if actual else False
        elif rule.operator == RuleOperator.MATCHES:
            return bool(re.match(expected, str(actual))) if actual else False
        elif rule.operator == RuleOperator.IN:
            return actual in expected if expected else False
        elif rule.operator == RuleOperator.NOT_IN:
            return actual not in expected if expected else True
        
        return False
    
    def _get_nested(self, obj: Dict, path: str) -> Any:
        """Get nested value using dot notation."""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
```

---

## Section 3: Rate Limiting

### Task 3.1: Rate Limiter

**File**: `apps/backend/governance/limits/rate_limiter.py`

```python
"""Rate limiting."""
import asyncio
import sqlite3
from typing import Optional, Dict, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from ..models import RateLimit

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, db_path: str = "rate_limits.db"):
        self.db_path = Path(db_path)
        self._limits: Dict[str, RateLimit] = {}
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_counts (
                    limit_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    count INTEGER NOT NULL,
                    window_start TEXT NOT NULL,
                    PRIMARY KEY (limit_id, target_id)
                )
            """)
    
    def configure(self, limit: RateLimit) -> None:
        """Configure a rate limit."""
        self._limits[limit.id] = limit
    
    async def check(
        self,
        limit_id: str,
        target_id: str
    ) -> Tuple[bool, int]:
        """Check if request is allowed.
        
        Returns:
            Tuple of (allowed, remaining)
        """
        limit = self._limits.get(limit_id)
        if not limit or not limit.enabled:
            return True, -1  # No limit
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=limit.window_seconds)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT count, window_start FROM rate_counts
                WHERE limit_id = ? AND target_id = ?
            """, (limit_id, target_id))
            
            row = cursor.fetchone()
            
            if not row:
                # First request
                return True, limit.max_count - 1
            
            stored_start = datetime.fromisoformat(row["window_start"])
            
            if stored_start < window_start:
                # Window expired, reset
                return True, limit.max_count - 1
            
            current = row["count"]
            remaining = limit.max_count - current - 1
            
            if current >= limit.max_count:
                return False, 0
            
            return True, remaining
    
    async def record(self, limit_id: str, target_id: str) -> None:
        """Record a request."""
        limit = self._limits.get(limit_id)
        if not limit:
            return
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=limit.window_seconds)
        
        with sqlite3.connect(self.db_path) as conn:
            # Check current window
            cursor = conn.execute("""
                SELECT count, window_start FROM rate_counts
                WHERE limit_id = ? AND target_id = ?
            """, (limit_id, target_id))
            
            row = cursor.fetchone()
            
            if not row or datetime.fromisoformat(row[1]) < window_start:
                # New window
                conn.execute("""
                    INSERT OR REPLACE INTO rate_counts
                    (limit_id, target_id, count, window_start)
                    VALUES (?, ?, 1, ?)
                """, (limit_id, target_id, now.isoformat()))
            else:
                # Increment existing
                conn.execute("""
                    UPDATE rate_counts
                    SET count = count + 1
                    WHERE limit_id = ? AND target_id = ?
                """, (limit_id, target_id))
```

---

### Task 3.2: Quota Manager

**File**: `apps/backend/governance/limits/quota_manager.py`

```python
"""Quota management."""
import sqlite3
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
from ..models import Quota

class QuotaManager:
    """Manages user resource quotas."""
    
    def __init__(self, db_path: str = "quotas.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quotas (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    limit_value REAL NOT NULL,
                    period TEXT NOT NULL,
                    current_usage REAL DEFAULT 0,
                    reset_at TEXT,
                    UNIQUE(user_id, resource)
                )
            """)
    
    async def set_quota(
        self,
        user_id: str,
        resource: str,
        limit: float,
        period: str = "monthly"
    ) -> Quota:
        """Set quota for a user."""
        import uuid
        
        reset_at = self._calculate_reset(period)
        quota = Quota(
            id=str(uuid.uuid4()),
            user_id=user_id,
            resource=resource,
            limit=limit,
            period=period,
            reset_at=reset_at,
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO quotas
                (id, user_id, resource, limit_value, period, current_usage, reset_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (
                quota.id,
                quota.user_id,
                quota.resource,
                quota.limit,
                quota.period,
                quota.reset_at,
            ))
        
        return quota
    
    async def check(
        self,
        user_id: str,
        resource: str,
        amount: float = 1.0
    ) -> Tuple[bool, float]:
        """Check if quota allows usage.
        
        Returns:
            Tuple of (allowed, remaining)
        """
        quota = await self.get(user_id, resource)
        if not quota:
            return True, float("inf")  # No quota
        
        # Check for reset
        if quota.reset_at and datetime.utcnow() > datetime.fromisoformat(quota.reset_at):
            await self._reset_quota(quota)
            quota.current_usage = 0
        
        remaining = quota.limit - quota.current_usage
        allowed = remaining >= amount
        
        return allowed, remaining
    
    async def consume(
        self,
        user_id: str,
        resource: str,
        amount: float = 1.0
    ) -> bool:
        """Consume quota."""
        allowed, _ = await self.check(user_id, resource, amount)
        if not allowed:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE quotas
                SET current_usage = current_usage + ?
                WHERE user_id = ? AND resource = ?
            """, (amount, user_id, resource))
        
        return True
    
    async def get(self, user_id: str, resource: str) -> Optional[Quota]:
        """Get quota for user/resource."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quotas
                WHERE user_id = ? AND resource = ?
            """, (user_id, resource))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Quota(
                id=row["id"],
                user_id=row["user_id"],
                resource=row["resource"],
                limit=row["limit_value"],
                period=row["period"],
                current_usage=row["current_usage"],
                reset_at=row["reset_at"],
            )
    
    def _calculate_reset(self, period: str) -> str:
        """Calculate next reset time."""
        now = datetime.utcnow()
        if period == "daily":
            reset = now + timedelta(days=1)
        elif period == "weekly":
            reset = now + timedelta(weeks=1)
        else:  # monthly
            reset = now + timedelta(days=30)
        return reset.isoformat()
    
    async def _reset_quota(self, quota: Quota) -> None:
        """Reset quota."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE quotas
                SET current_usage = 0, reset_at = ?
                WHERE id = ?
            """, (self._calculate_reset(quota.period), quota.id))
```

---

## Section 4: Approval Workflows

### Task 4.1: Approval Workflow

**File**: `apps/backend/governance/workflow/approval_workflow.py`

```python
"""Approval workflow management."""
import sqlite3
import json
from typing import Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import uuid
from ..models import ApprovalRequest, ApprovalStatus

class ApprovalWorkflow:
    """Manages approval requests."""
    
    def __init__(self, db_path: str = "approvals.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    request_type TEXT NOT NULL,
                    requester_id TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    context TEXT,
                    approvers TEXT,
                    approved_by TEXT,
                    rejected_by TEXT,
                    rejection_reason TEXT,
                    created_at TEXT,
                    expires_at TEXT,
                    completed_at TEXT
                )
            """)
    
    async def request_approval(
        self,
        request_type: str,
        requester_id: str,
        description: str,
        approvers: List[str],
        context: Optional[dict] = None,
        expires_hours: int = 48
    ) -> ApprovalRequest:
        """Create an approval request."""
        now = datetime.utcnow()
        
        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            request_type=request_type,
            requester_id=requester_id,
            description=description,
            approvers=approvers,
            context=context or {},
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=expires_hours)).isoformat(),
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO approvals
                (id, request_type, requester_id, description, status,
                 context, approvers, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.id,
                request.request_type,
                request.requester_id,
                request.description,
                request.status.value,
                json.dumps(request.context),
                json.dumps(request.approvers),
                request.created_at,
                request.expires_at,
            ))
        
        return request
    
    async def approve(
        self,
        request_id: str,
        approver_id: str
    ) -> bool:
        """Approve a request."""
        request = await self.get(request_id)
        if not request:
            return False
        
        if request.status != ApprovalStatus.PENDING:
            return False
        
        if approver_id not in request.approvers:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE approvals
                SET status = ?, approved_by = ?, completed_at = ?
                WHERE id = ?
            """, (
                ApprovalStatus.APPROVED.value,
                approver_id,
                datetime.utcnow().isoformat(),
                request_id,
            ))
        
        return True
    
    async def reject(
        self,
        request_id: str,
        rejector_id: str,
        reason: str
    ) -> bool:
        """Reject a request."""
        request = await self.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        if rejector_id not in request.approvers:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE approvals
                SET status = ?, rejected_by = ?, rejection_reason = ?, completed_at = ?
                WHERE id = ?
            """, (
                ApprovalStatus.REJECTED.value,
                rejector_id,
                reason,
                datetime.utcnow().isoformat(),
                request_id,
            ))
        
        return True
    
    async def get(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM approvals WHERE id = ?", (request_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ApprovalRequest(
                id=row["id"],
                request_type=row["request_type"],
                requester_id=row["requester_id"],
                description=row["description"],
                status=ApprovalStatus(row["status"]),
                context=json.loads(row["context"] or "{}"),
                approvers=json.loads(row["approvers"] or "[]"),
                approved_by=row["approved_by"],
                rejected_by=row["rejected_by"],
                rejection_reason=row["rejection_reason"],
                created_at=row["created_at"],
                expires_at=row["expires_at"],
                completed_at=row["completed_at"],
            )
    
    async def get_pending(self, approver_id: str) -> List[ApprovalRequest]:
        """Get pending requests for an approver."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM approvals
                WHERE status = ? AND approvers LIKE ?
                ORDER BY created_at DESC
            """, (ApprovalStatus.PENDING.value, f'%"{approver_id}"%'))
            
            return [self._row_to_request(row) for row in cursor.fetchall()]
```

---

## Validation Checklist

- [ ] Policy engine evaluates rules correctly
- [ ] Rate limiting enforced
- [ ] Quota tracking works
- [ ] Approval workflow creates/approves/rejects
- [ ] Expiration handling works
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 3 (Auth), Phase 6 (Security)

**Enables**: Phase 10 (Testing/Docs)

---

## ADR References

- ADR-008: Feature Consolidation
- ADR-010: Security Model Harmonization

---

*Phase 9 Specification v1.0.0*
