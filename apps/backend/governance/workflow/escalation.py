"""
Escalation Management - Phase 9 Implementation.

Handles escalation rules and automatic escalation.

World-Class Standards:
- Configurable escalation paths
- Time-based triggers
- Notification integration
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from ..models import ApprovalRequest, ApprovalStatus, SUPPORTED_PROVIDERS


logger = logging.getLogger(__name__)


class EscalationTrigger(Enum):
    """Triggers for escalation."""
    TIME_EXCEEDED = "time_exceeded"
    NO_RESPONSE = "no_response"
    MANUAL = "manual"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class EscalationRule:
    """Rule for escalation."""
    id: str
    name: str
    trigger: EscalationTrigger
    threshold_hours: int
    escalate_to: List[str]
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationEvent:
    """Record of an escalation event."""
    request_id: str
    rule_id: str
    trigger: EscalationTrigger
    escalated_to: str
    timestamp: datetime
    previous_state: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# DEFAULT ESCALATION RULES
# =============================================================================

DEFAULT_ESCALATION_RULES: Dict[str, EscalationRule] = {
    "24h_no_response": EscalationRule(
        id="24h_no_response",
        name="24 Hour No Response",
        trigger=EscalationTrigger.NO_RESPONSE,
        threshold_hours=24,
        escalate_to=["manager"],
        priority=1,
    ),
    "48h_pending": EscalationRule(
        id="48h_pending",
        name="48 Hour Pending",
        trigger=EscalationTrigger.TIME_EXCEEDED,
        threshold_hours=48,
        escalate_to=["director"],
        priority=2,
    ),
    "urgent_high_cost": EscalationRule(
        id="urgent_high_cost",
        name="Urgent High Cost",
        trigger=EscalationTrigger.POLICY_VIOLATION,
        threshold_hours=4,
        escalate_to=["finance", "manager"],
        priority=3,
    ),
}


class EscalationManager:
    """
    Manages escalation rules and execution.
    """
    
    def __init__(self) -> None:
        self._rules: Dict[str, EscalationRule] = {}
        self._events: Dict[str, List[EscalationEvent]] = {}
        self._notification_callbacks: List[Callable] = []
        self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default escalation rules."""
        for rule_id, rule in DEFAULT_ESCALATION_RULES.items():
            self._rules[rule_id] = rule
        logger.info(f"Loaded {len(self._rules)} default escalation rules")
    
    def register_rule(self, rule: EscalationRule) -> None:
        """Register an escalation rule."""
        self._rules[rule.id] = rule
        logger.info(f"Registered escalation rule: {rule.id}")
    
    def unregister_rule(self, rule_id: str) -> bool:
        """Unregister an escalation rule."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False
    
    def add_notification_callback(self, callback: Callable) -> None:
        """Add callback for escalation notifications."""
        self._notification_callbacks.append(callback)
    
    def check_escalation(self, request: ApprovalRequest) -> Optional[EscalationEvent]:
        """Check if a request needs escalation."""
        if request.status != ApprovalStatus.PENDING:
            return None
        
        age_hours = (datetime.utcnow() - request.created_at).total_seconds() / 3600
        
        # Check rules in priority order
        sorted_rules = sorted(
            self._rules.values(),
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            should_escalate = False
            
            if rule.trigger == EscalationTrigger.TIME_EXCEEDED:
                should_escalate = age_hours >= rule.threshold_hours
            elif rule.trigger == EscalationTrigger.NO_RESPONSE:
                # Check if any step has responded
                any_response = any(
                    s.approver is not None for s in request.steps
                )
                should_escalate = not any_response and age_hours >= rule.threshold_hours
            
            if should_escalate:
                return self._create_escalation(request, rule)
        
        return None
    
    def _create_escalation(
        self,
        request: ApprovalRequest,
        rule: EscalationRule
    ) -> EscalationEvent:
        """Create an escalation event."""
        escalate_to = rule.escalate_to[0] if rule.escalate_to else "admin"
        
        event = EscalationEvent(
            request_id=request.id,
            rule_id=rule.id,
            trigger=rule.trigger,
            escalated_to=escalate_to,
            timestamp=datetime.utcnow(),
            previous_state=str(request.status.value),
        )
        
        # Record event
        if request.id not in self._events:
            self._events[request.id] = []
        self._events[request.id].append(event)
        
        # Notify callbacks
        self._notify(event)
        
        logger.info(
            f"Escalated request {request.id} to {escalate_to} "
            f"(rule: {rule.id})"
        )
        
        return event
    
    def _notify(self, event: EscalationEvent) -> None:
        """Notify registered callbacks."""
        for callback in self._notification_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")
    
    def escalate_manually(
        self,
        request: ApprovalRequest,
        escalate_to: str,
        reason: str
    ) -> EscalationEvent:
        """Manually escalate a request."""
        event = EscalationEvent(
            request_id=request.id,
            rule_id="manual",
            trigger=EscalationTrigger.MANUAL,
            escalated_to=escalate_to,
            timestamp=datetime.utcnow(),
            previous_state=str(request.status.value),
            metadata={"reason": reason},
        )
        
        if request.id not in self._events:
            self._events[request.id] = []
        self._events[request.id].append(event)
        
        self._notify(event)
        
        logger.info(f"Manually escalated request {request.id} to {escalate_to}")
        return event
    
    def get_escalation_history(self, request_id: str) -> List[EscalationEvent]:
        """Get escalation history for a request."""
        return self._events.get(request_id, [])
    
    def process_pending_escalations(
        self,
        requests: List[ApprovalRequest]
    ) -> List[EscalationEvent]:
        """Process all pending requests for escalations."""
        events = []
        for request in requests:
            event = self.check_escalation(request)
            if event:
                events.append(event)
        
        if events:
            logger.info(f"Processed {len(events)} escalations")
        return events
    
    def list_rules(self) -> List[EscalationRule]:
        """List all escalation rules."""
        return list(self._rules.values())
    
    def get_rule(self, rule_id: str) -> Optional[EscalationRule]:
        """Get an escalation rule by ID."""
        return self._rules.get(rule_id)
