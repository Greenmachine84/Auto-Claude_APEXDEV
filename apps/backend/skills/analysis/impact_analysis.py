"""Impact analysis skill.

Analyzes impact of code changes.

Capabilities:
- Identify affected files
- Trace dependencies
- Assess risk level
- Suggest test coverage
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


class RiskLevel(Enum):
    """Risk level of a change."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class AffectedFile:
    """A file affected by changes."""
    file_path: str
    impact_type: str  # direct, indirect, transitive
    reason: str
    risk_level: RiskLevel


@dataclass
class ImpactReport:
    """Impact analysis report."""
    changed_files: List[str]
    affected_files: List[AffectedFile]
    overall_risk: RiskLevel
    suggested_tests: List[str] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)


class ImpactAnalysisSkill(BaseSkill):
    """Analyze impact of code changes.
    
    Determines what parts of the codebase are affected by
    changes and assesses the risk level.
    
    Example:
        skill = ImpactAnalysisSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "changed_files": ["src/core.py"],
                "change_type": "modification",
            }
        )
        result = await skill.run(context)
    """
    
    name = "impact_analysis"
    description = "Analyze impact of code changes"
    category = SkillCategory.ANALYSIS
    required_tools = ["file_read", "grep_search"]
    required_permissions = {"read_files"}
    version = "1.0.0"
    
    # Risk factors
    HIGH_RISK_PATHS = ["core", "auth", "security", "database", "api"]
    MEDIUM_RISK_PATHS = ["service", "handler", "controller", "model"]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "changed_files" not in input_data and "diff" not in input_data:
            return False
        return True
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute impact analysis.
        
        Args:
            context: Execution context with changes
            
        Returns:
            SkillResult with impact report
        """
        input_data = context.input_data
        changed_files = input_data.get("changed_files", [])
        change_type = input_data.get("change_type", "modification")
        
        # Find affected files
        affected = self._find_affected_files(changed_files)
        
        # Assess risk
        overall_risk = self._assess_overall_risk(changed_files, affected)
        
        # Suggest tests
        suggested_tests = self._suggest_tests(changed_files, affected)
        
        # Check for breaking changes
        breaking = self._find_breaking_changes(changed_files, change_type)
        
        report = ImpactReport(
            changed_files=changed_files,
            affected_files=affected,
            overall_risk=overall_risk,
            suggested_tests=suggested_tests,
            breaking_changes=breaking,
        )
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "changed_file_count": len(changed_files),
                "affected_file_count": len(affected),
                "overall_risk": overall_risk.value,
                "affected_files": [self._affected_to_dict(a) for a in affected],
                "suggested_tests": suggested_tests,
                "breaking_changes": breaking,
            },
            tokens_used=0,
        )
    
    def _find_affected_files(self, changed_files: List[str]) -> List[AffectedFile]:
        """Find files affected by changes."""
        affected = []
        # Placeholder - will use dependency graph
        return affected
    
    def _assess_overall_risk(self, changed: List[str], affected: List[AffectedFile]) -> RiskLevel:
        """Assess overall risk of changes."""
        # Check high-risk paths
        for path in changed:
            for risk_path in self.HIGH_RISK_PATHS:
                if risk_path in path.lower():
                    return RiskLevel.HIGH
        
        for path in changed:
            for risk_path in self.MEDIUM_RISK_PATHS:
                if risk_path in path.lower():
                    return RiskLevel.MEDIUM
        
        if len(affected) > 10:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _suggest_tests(self, changed: List[str], affected: List[AffectedFile]) -> List[str]:
        """Suggest tests to run."""
        tests = []
        for file_path in changed:
            test_path = file_path.replace("src/", "tests/").replace(".py", "_test.py")
            tests.append(test_path)
        return tests
    
    def _find_breaking_changes(self, changed: List[str], change_type: str) -> List[str]:
        """Find potential breaking changes."""
        # Placeholder
        return []
    
    def _affected_to_dict(self, affected: AffectedFile) -> Dict[str, Any]:
        """Convert AffectedFile to dictionary."""
        return {
            "file_path": affected.file_path,
            "impact_type": affected.impact_type,
            "reason": affected.reason,
            "risk_level": affected.risk_level.value,
        }
