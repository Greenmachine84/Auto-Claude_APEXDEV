"""Architecture review skill.

Assesses code architecture and design.

Capabilities:
- Evaluate architecture patterns
- Identify design issues
- Assess modularity
- Check SOLID principles
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


class ArchitecturePattern(Enum):
    """Common architecture patterns."""
    MVC = "mvc"
    MVVM = "mvvm"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    EVENT_DRIVEN = "event_driven"
    CQRS = "cqrs"


class DesignPrinciple(Enum):
    """Design principles to check."""
    SINGLE_RESPONSIBILITY = "srp"
    OPEN_CLOSED = "ocp"
    LISKOV_SUBSTITUTION = "lsp"
    INTERFACE_SEGREGATION = "isp"
    DEPENDENCY_INVERSION = "dip"
    DRY = "dry"
    KISS = "kiss"
    YAGNI = "yagni"


@dataclass
class ArchitectureFinding:
    """An architecture review finding."""
    title: str
    description: str
    principle: Optional[DesignPrinciple] = None
    severity: str = "medium"
    suggestion: Optional[str] = None
    affected_files: List[str] = field(default_factory=list)


class ArchitectureReviewSkill(BaseSkill):
    """Assess code architecture and design.
    
    Evaluates code against architecture patterns and
    design principles like SOLID.
    
    Example:
        skill = ArchitectureReviewSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "files": ["src/main.py", "src/utils.py"],
                "check_solid": True,
            }
        )
        result = await skill.run(context)
    """
    
    name = "architecture_review"
    description = "Architecture and design assessment"
    category = SkillCategory.REVIEW
    required_tools = ["file_read", "directory_list"]
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "files" not in input_data and "code" not in input_data:
            return False
        return True
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute architecture review.
        
        Args:
            context: Execution context with files to review
            
        Returns:
            SkillResult with architecture findings
        """
        input_data = context.input_data
        files = input_data.get("files", [])
        check_solid = input_data.get("check_solid", True)
        
        # Detect architecture pattern
        pattern = self._detect_pattern(files)
        
        # Check design principles
        findings = []
        if check_solid:
            findings.extend(self._check_solid_principles(files))
        
        # Calculate architecture score
        score = self._calculate_score(findings)
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "architecture_score": score,
                "detected_pattern": pattern.value if pattern else None,
                "findings": [self._finding_to_dict(f) for f in findings],
                "finding_count": len(findings),
                "solid_compliance": self._calculate_solid_compliance(findings),
            },
            tokens_used=0,
        )
    
    def _detect_pattern(self, files: List[str]) -> Optional[ArchitecturePattern]:
        """Detect architecture pattern from file structure."""
        # Placeholder - will analyze file structure
        return None
    
    def _check_solid_principles(self, files: List[str]) -> List[ArchitectureFinding]:
        """Check SOLID principles compliance."""
        # Placeholder - will use LLM for analysis
        return []
    
    def _calculate_score(self, findings: List[ArchitectureFinding]) -> float:
        """Calculate architecture score."""
        if not findings:
            return 100.0
        
        deductions = {"critical": 20, "high": 12, "medium": 6, "low": 2}
        total = sum(deductions.get(f.severity, 0) for f in findings)
        return max(0.0, 100.0 - total)
    
    def _calculate_solid_compliance(self, findings: List[ArchitectureFinding]) -> Dict[str, bool]:
        """Calculate compliance for each SOLID principle."""
        violations = {f.principle for f in findings if f.principle}
        return {
            "srp": DesignPrinciple.SINGLE_RESPONSIBILITY not in violations,
            "ocp": DesignPrinciple.OPEN_CLOSED not in violations,
            "lsp": DesignPrinciple.LISKOV_SUBSTITUTION not in violations,
            "isp": DesignPrinciple.INTERFACE_SEGREGATION not in violations,
            "dip": DesignPrinciple.DEPENDENCY_INVERSION not in violations,
        }
    
    def _finding_to_dict(self, finding: ArchitectureFinding) -> Dict[str, Any]:
        """Convert ArchitectureFinding to dictionary."""
        return {
            "title": finding.title,
            "description": finding.description,
            "principle": finding.principle.value if finding.principle else None,
            "severity": finding.severity,
            "suggestion": finding.suggestion,
            "affected_files": finding.affected_files,
        }
