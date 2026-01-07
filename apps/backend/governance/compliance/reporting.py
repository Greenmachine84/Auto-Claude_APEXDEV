"""
Compliance Reporting - Phase 9 Implementation.

Generates compliance reports for governance.

World-Class Standards:
- SOC 2 format
- GDPR ready
- Executive summaries
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path

from ..models import ComplianceReport, SUPPORTED_PROVIDERS
from .compliance_logger import ComplianceLogger, ComplianceLogEntry
from .audit_trail import AuditTrail, AuditEntry


logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"


class ReportPeriod(Enum):
    """Report time periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


@dataclass
class ReportSection:
    """Section of a compliance report."""
    title: str
    summary: str
    data: Dict[str, Any]
    findings: List[str]
    recommendations: List[str]


@dataclass
class GovernanceReport:
    """Complete governance compliance report."""
    id: str
    title: str
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    sections: List[ReportSection]
    executive_summary: str
    risk_score: float
    compliance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceReporter:
    """
    Generates compliance reports.
    
    Provides:
    - SOC 2 format reports
    - Executive summaries
    - Risk scoring
    """
    
    def __init__(
        self,
        compliance_logger: Optional[ComplianceLogger] = None,
        audit_trail: Optional[AuditTrail] = None,
    ) -> None:
        self._logger = compliance_logger or ComplianceLogger()
        self._audit = audit_trail or AuditTrail()
    
    def generate_report(
        self,
        period: ReportPeriod = ReportPeriod.MONTHLY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> GovernanceReport:
        """
        Generate a governance compliance report.
        
        Args:
            period: Report period type
            start_date: Start of period
            end_date: End of period
            
        Returns:
            Generated report
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or self._get_period_start(period, end_date)
        
        # Collect data
        log_entries = self._logger.get_entries(
            start_time=start_date,
            end_time=end_date,
        )
        audit_entries = self._audit.get_entries(
            start_time=start_date,
            end_time=end_date,
        )
        
        # Generate sections
        sections = [
            self._generate_policy_section(log_entries),
            self._generate_access_section(log_entries),
            self._generate_rate_limit_section(log_entries),
            self._generate_approval_section(log_entries),
            self._generate_audit_section(audit_entries),
        ]
        
        # Calculate scores
        compliance_score = self._calculate_compliance_score(log_entries)
        risk_score = self._calculate_risk_score(log_entries, audit_entries)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            sections, compliance_score, risk_score
        )
        
        report_id = f"GOV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return GovernanceReport(
            id=report_id,
            title=f"Governance Compliance Report - {period.value.title()}",
            period=period,
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.utcnow(),
            sections=sections,
            executive_summary=executive_summary,
            risk_score=risk_score,
            compliance_score=compliance_score,
            metadata={
                "log_entries": len(log_entries),
                "audit_entries": len(audit_entries),
                "providers": list(SUPPORTED_PROVIDERS),
            },
        )
    
    def _get_period_start(
        self,
        period: ReportPeriod,
        end_date: datetime
    ) -> datetime:
        """Calculate period start date."""
        if period == ReportPeriod.DAILY:
            return end_date - timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif period == ReportPeriod.MONTHLY:
            return end_date - timedelta(days=30)
        elif period == ReportPeriod.QUARTERLY:
            return end_date - timedelta(days=90)
        else:  # ANNUAL
            return end_date - timedelta(days=365)
    
    def _generate_policy_section(
        self,
        entries: List[ComplianceLogEntry]
    ) -> ReportSection:
        """Generate policy evaluation section."""
        policy_entries = [
            e for e in entries
            if "policy" in e.action.lower()
        ]
        
        total = len(policy_entries)
        allowed = sum(1 for e in policy_entries if e.result == "allowed")
        denied = total - allowed
        
        findings = []
        if denied > 0:
            findings.append(f"{denied} policy violations detected")
        if total == 0:
            findings.append("No policy evaluations recorded")
        
        recommendations = []
        if denied > total * 0.1:
            recommendations.append("Review frequently violated policies")
        
        return ReportSection(
            title="Policy Compliance",
            summary=f"{allowed}/{total} requests compliant ({100*allowed/max(total,1):.1f}%)",
            data={
                "total_evaluations": total,
                "allowed": allowed,
                "denied": denied,
                "compliance_rate": allowed / max(total, 1),
            },
            findings=findings,
            recommendations=recommendations,
        )
    
    def _generate_access_section(
        self,
        entries: List[ComplianceLogEntry]
    ) -> ReportSection:
        """Generate access control section."""
        access_entries = [
            e for e in entries
            if "access" in e.action.lower()
        ]
        
        granted = sum(1 for e in access_entries if e.result == "granted")
        denied = len(access_entries) - granted
        
        # Group by provider
        by_provider: Dict[str, int] = {}
        for entry in access_entries:
            by_provider[entry.provider] = by_provider.get(entry.provider, 0) + 1
        
        findings = []
        if denied > 10:
            findings.append(f"High number of access denials: {denied}")
        
        return ReportSection(
            title="Access Control",
            summary=f"{granted} access grants, {denied} denials",
            data={
                "total_requests": len(access_entries),
                "granted": granted,
                "denied": denied,
                "by_provider": by_provider,
            },
            findings=findings,
            recommendations=[],
        )
    
    def _generate_rate_limit_section(
        self,
        entries: List[ComplianceLogEntry]
    ) -> ReportSection:
        """Generate rate limiting section."""
        rate_entries = [
            e for e in entries
            if "rate" in e.action.lower()
        ]
        
        limited = sum(1 for e in rate_entries if e.result == "limited")
        
        findings = []
        if limited > 0:
            findings.append(f"{limited} requests rate limited")
        
        return ReportSection(
            title="Rate Limiting",
            summary=f"{len(rate_entries)} rate checks, {limited} limited",
            data={
                "total_checks": len(rate_entries),
                "rate_limited": limited,
            },
            findings=findings,
            recommendations=["Consider increasing limits" if limited > 100 else ""],
        )
    
    def _generate_approval_section(
        self,
        entries: List[ComplianceLogEntry]
    ) -> ReportSection:
        """Generate approval workflow section."""
        approval_entries = [
            e for e in entries
            if "approval" in e.action.lower()
        ]
        
        approved = sum(1 for e in approval_entries if "approved" in e.result)
        rejected = sum(1 for e in approval_entries if "rejected" in e.result)
        pending = len(approval_entries) - approved - rejected
        
        return ReportSection(
            title="Approval Workflows",
            summary=f"{approved} approved, {rejected} rejected, {pending} pending",
            data={
                "total_requests": len(approval_entries),
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
            },
            findings=[],
            recommendations=[],
        )
    
    def _generate_audit_section(
        self,
        entries: List[AuditEntry]
    ) -> ReportSection:
        """Generate audit trail section."""
        # Count by action type
        action_counts: Dict[str, int] = {}
        for entry in entries:
            action = entry.action.split("_")[0]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return ReportSection(
            title="Audit Trail",
            summary=f"{len(entries)} audit events recorded",
            data={
                "total_events": len(entries),
                "by_action": action_counts,
            },
            findings=[],
            recommendations=[],
        )
    
    def _calculate_compliance_score(
        self,
        entries: List[ComplianceLogEntry]
    ) -> float:
        """Calculate overall compliance score (0-100)."""
        if not entries:
            return 100.0
        
        violations = sum(
            1 for e in entries
            if e.result in ("denied", "limited", "rejected")
        )
        
        return max(0, 100 - (violations / len(entries) * 100))
    
    def _calculate_risk_score(
        self,
        log_entries: List[ComplianceLogEntry],
        audit_entries: List[AuditEntry]
    ) -> float:
        """Calculate risk score (0-100, lower is better)."""
        risk = 0.0
        
        # Policy violations increase risk
        violations = sum(
            1 for e in log_entries if e.result == "denied"
        )
        risk += min(violations * 2, 30)
        
        # Configuration changes increase risk
        config_changes = sum(
            1 for e in audit_entries if "config" in e.action
        )
        risk += min(config_changes * 5, 20)
        
        # High volume increases risk
        if len(log_entries) > 10000:
            risk += 10
        
        return min(risk, 100)
    
    def _generate_executive_summary(
        self,
        sections: List[ReportSection],
        compliance_score: float,
        risk_score: float
    ) -> str:
        """Generate executive summary."""
        summary_parts = [
            f"Compliance Score: {compliance_score:.1f}%",
            f"Risk Score: {risk_score:.1f}/100",
            "",
            "Key Findings:",
        ]
        
        for section in sections:
            for finding in section.findings:
                if finding:
                    summary_parts.append(f"- {finding}")
        
        if not any(s.findings for s in sections):
            summary_parts.append("- No significant findings")
        
        return "\n".join(summary_parts)
    
    def export_report(
        self,
        report: GovernanceReport,
        path: str,
        format: ReportFormat = ReportFormat.JSON
    ) -> None:
        """Export report to file."""
        if format == ReportFormat.JSON:
            self._export_json(report, path)
        elif format == ReportFormat.MARKDOWN:
            self._export_markdown(report, path)
        else:
            self._export_json(report, path)
    
    def _export_json(self, report: GovernanceReport, path: str) -> None:
        """Export as JSON."""
        data = {
            "id": report.id,
            "title": report.title,
            "period": report.period.value,
            "start_date": report.start_date.isoformat(),
            "end_date": report.end_date.isoformat(),
            "generated_at": report.generated_at.isoformat(),
            "compliance_score": report.compliance_score,
            "risk_score": report.risk_score,
            "executive_summary": report.executive_summary,
            "sections": [
                {
                    "title": s.title,
                    "summary": s.summary,
                    "data": s.data,
                    "findings": s.findings,
                    "recommendations": s.recommendations,
                }
                for s in report.sections
            ],
            "metadata": report.metadata,
        }
        Path(path).write_text(json.dumps(data, indent=2))
        logger.info(f"Exported report to {path}")
    
    def _export_markdown(self, report: GovernanceReport, path: str) -> None:
        """Export as Markdown."""
        lines = [
            f"# {report.title}",
            "",
            f"**Period:** {report.start_date.date()} to {report.end_date.date()}",
            f"**Generated:** {report.generated_at.isoformat()}",
            "",
            "## Executive Summary",
            "",
            report.executive_summary,
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Compliance Score | {report.compliance_score:.1f}% |",
            f"| Risk Score | {report.risk_score:.1f}/100 |",
            "",
        ]
        
        for section in report.sections:
            lines.extend([
                f"## {section.title}",
                "",
                section.summary,
                "",
            ])
            
            if section.findings:
                lines.append("### Findings")
                for finding in section.findings:
                    if finding:
                        lines.append(f"- {finding}")
                lines.append("")
        
        Path(path).write_text("\n".join(lines))
        logger.info(f"Exported markdown report to {path}")
