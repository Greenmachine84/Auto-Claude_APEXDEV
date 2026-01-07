"""Threat detection for security events.

World-Class Standards:
- Real-time threat detection
- Pattern-based analysis
- Anomaly detection support
- Alert generation
"""
import re
import uuid
from typing import List, Dict, Optional, Set, Callable
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

from ..models import SecurityFinding, ThreatType, Severity


@dataclass
class ThreatSignature:
    """Signature for threat detection."""
    id: str
    name: str
    threat_type: ThreatType
    severity: Severity
    pattern: str
    description: str
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class ThreatAlert:
    """Generated threat alert."""
    id: str
    timestamp: str
    signature_id: str
    threat_type: ThreatType
    severity: Severity
    message: str
    source: str
    evidence: Optional[str] = None
    context: Dict = field(default_factory=dict)


class ThreatDetector:
    """Real-time threat detection engine.
    
    Provides:
    - Signature-based detection
    - Pattern matching
    - Alert generation
    - Callback hooks
    
    Example:
        detector = ThreatDetector()
        
        # Register alert callback
        detector.on_threat(lambda alert: print(f"ALERT: {alert.message}"))
        
        # Scan content
        findings = await detector.scan(content)
    """
    
    # Built-in threat signatures
    BUILT_IN_SIGNATURES: List[ThreatSignature] = [
        # Prompt injection signatures
        ThreatSignature(
            id="pi_ignore_instructions",
            name="Ignore Instructions Attack",
            threat_type=ThreatType.PROMPT_INJECTION,
            severity=Severity.HIGH,
            pattern=r"(?i)ignore\s+(all\s+)?previous\s+instructions?",
            description="Attempt to override system instructions",
            tags=["injection", "llm"],
        ),
        ThreatSignature(
            id="pi_jailbreak",
            name="Jailbreak Attempt",
            threat_type=ThreatType.PROMPT_INJECTION,
            severity=Severity.CRITICAL,
            pattern=r"(?i)(jailbreak|dan\s+mode|dev\s+mode)",
            description="Jailbreak attempt detected",
            tags=["injection", "jailbreak"],
        ),
        ThreatSignature(
            id="pi_role_hijack",
            name="Role Hijacking",
            threat_type=ThreatType.PROMPT_INJECTION,
            severity=Severity.HIGH,
            pattern=r"(?i)you\s+are\s+now\s+(a\s+)?different",
            description="Role hijacking attempt",
            tags=["injection", "role"],
        ),
        
        # Secret exposure signatures
        ThreatSignature(
            id="secret_api_key",
            name="API Key Exposure",
            threat_type=ThreatType.SECRET_EXPOSED,
            severity=Severity.CRITICAL,
            pattern=r"sk-[A-Za-z0-9]{48,}",
            description="OpenAI API key detected",
            tags=["secret", "openai"],
        ),
        ThreatSignature(
            id="secret_github",
            name="GitHub Token Exposure",
            threat_type=ThreatType.SECRET_EXPOSED,
            severity=Severity.CRITICAL,
            pattern=r"gh[pousr]_[A-Za-z0-9_]{36,}",
            description="GitHub token detected",
            tags=["secret", "github"],
        ),
        
        # Code injection signatures
        ThreatSignature(
            id="code_sql_injection",
            name="SQL Injection",
            threat_type=ThreatType.CODE_INJECTION,
            severity=Severity.CRITICAL,
            pattern=r"(?i)('\s*(OR|AND)\s*'|UNION\s+SELECT|--\s*$)",
            description="SQL injection pattern detected",
            tags=["injection", "sql"],
        ),
        ThreatSignature(
            id="code_xss",
            name="Cross-Site Scripting",
            threat_type=ThreatType.CODE_INJECTION,
            severity=Severity.HIGH,
            pattern=r"<script[^>]*>|javascript:\s*",
            description="XSS pattern detected",
            tags=["injection", "xss"],
        ),
        
        # Data leak signatures
        ThreatSignature(
            id="data_ssn",
            name="SSN Exposure",
            threat_type=ThreatType.DATA_LEAK,
            severity=Severity.CRITICAL,
            pattern=r"\b[0-9]{3}[-]?[0-9]{2}[-]?[0-9]{4}\b",
            description="Social Security Number detected",
            tags=["pii", "ssn"],
        ),
        ThreatSignature(
            id="data_credit_card",
            name="Credit Card Exposure",
            threat_type=ThreatType.DATA_LEAK,
            severity=Severity.CRITICAL,
            pattern=r"\b(?:[0-9]{4}[-. ]?){3}[0-9]{4}\b",
            description="Credit card number detected",
            tags=["pii", "financial"],
        ),
    ]
    
    def __init__(self):
        """Initialize threat detector."""
        self._signatures: Dict[str, ThreatSignature] = {}
        self._compiled: Dict[str, re.Pattern] = {}
        self._alert_callbacks: List[Callable[[ThreatAlert], None]] = []
        self._stats: Dict[str, int] = defaultdict(int)
        
        # Load built-in signatures
        for sig in self.BUILT_IN_SIGNATURES:
            self.add_signature(sig)
    
    def add_signature(self, signature: ThreatSignature) -> None:
        """Add a threat signature.
        
        Args:
            signature: Signature to add
        """
        self._signatures[signature.id] = signature
        try:
            self._compiled[signature.id] = re.compile(signature.pattern)
        except re.error:
            pass
    
    def remove_signature(self, signature_id: str) -> bool:
        """Remove a threat signature.
        
        Args:
            signature_id: ID of signature to remove
            
        Returns:
            True if removed
        """
        if signature_id in self._signatures:
            del self._signatures[signature_id]
            if signature_id in self._compiled:
                del self._compiled[signature_id]
            return True
        return False
    
    def on_threat(self, callback: Callable[[ThreatAlert], None]) -> None:
        """Register callback for threat alerts.
        
        Args:
            callback: Function to call when threat detected
        """
        self._alert_callbacks.append(callback)
    
    async def scan(
        self,
        content: str,
        source: str = "input",
        context: Optional[Dict] = None,
    ) -> List[SecurityFinding]:
        """Scan content for threats.
        
        Args:
            content: Content to scan
            source: Source identifier
            context: Additional context
            
        Returns:
            List of security findings
        """
        findings = []
        context = context or {}
        
        for sig_id, compiled in self._compiled.items():
            sig = self._signatures[sig_id]
            
            if not sig.enabled:
                continue
            
            for match in compiled.finditer(content):
                # Create finding
                finding = SecurityFinding(
                    id=str(uuid.uuid4()),
                    threat_type=sig.threat_type,
                    severity=sig.severity,
                    message=sig.description,
                    source=source,
                    evidence=self._redact_evidence(match.group()),
                )
                findings.append(finding)
                
                # Generate alert
                alert = ThreatAlert(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    signature_id=sig_id,
                    threat_type=sig.threat_type,
                    severity=sig.severity,
                    message=sig.description,
                    source=source,
                    evidence=self._redact_evidence(match.group()),
                    context=context,
                )
                
                # Notify callbacks
                for callback in self._alert_callbacks:
                    try:
                        callback(alert)
                    except Exception:
                        pass
                
                # Update stats
                self._stats[sig_id] += 1
        
        return findings
    
    def _redact_evidence(self, evidence: str, keep_chars: int = 4) -> str:
        """Redact sensitive evidence for safe logging."""
        if len(evidence) <= keep_chars * 2:
            return "*" * len(evidence)
        return evidence[:keep_chars] + "*" * (len(evidence) - keep_chars * 2) + evidence[-keep_chars:]
    
    def scan_sync(
        self,
        content: str,
        source: str = "input",
    ) -> List[SecurityFinding]:
        """Synchronous version of scan.
        
        Args:
            content: Content to scan
            source: Source identifier
            
        Returns:
            List of security findings
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        
        return loop.run_until_complete(self.scan(content, source))
    
    def get_stats(self) -> Dict[str, int]:
        """Get detection statistics.
        
        Returns:
            Dict of signature_id -> detection count
        """
        return dict(self._stats)
    
    def get_signatures_by_type(
        self,
        threat_type: ThreatType,
    ) -> List[ThreatSignature]:
        """Get signatures by threat type.
        
        Args:
            threat_type: Type to filter by
            
        Returns:
            List of matching signatures
        """
        return [
            sig for sig in self._signatures.values()
            if sig.threat_type == threat_type
        ]
    
    def get_signatures_by_tag(self, tag: str) -> List[ThreatSignature]:
        """Get signatures by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of matching signatures
        """
        return [
            sig for sig in self._signatures.values()
            if tag in sig.tags
        ]
    
    def enable_signature(self, signature_id: str) -> bool:
        """Enable a signature."""
        if signature_id in self._signatures:
            self._signatures[signature_id].enabled = True
            return True
        return False
    
    def disable_signature(self, signature_id: str) -> bool:
        """Disable a signature."""
        if signature_id in self._signatures:
            self._signatures[signature_id].enabled = False
            return True
        return False
    
    def list_signatures(self) -> List[ThreatSignature]:
        """List all registered signatures."""
        return list(self._signatures.values())
