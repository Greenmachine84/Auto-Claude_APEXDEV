"""Code Review Agent for automated PR and code review.

World-Class Standards:
- Expert-level code review
- Structured feedback
- LLM-agnostic execution

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from typing import Any, ClassVar, Dict, List, Optional
import json
import uuid

from ..base_enterprise_agent import BaseEnterpriseAgent, LLMRouter
from ..config import AgentCapability, EnterpriseAgentConfig
from ..types import (
    CodeReviewResult,
    EnterpriseAgentType,
    Finding,
    Severity,
    Suggestion,
)
from .review_result import ReviewResult, ReviewFinding, ReviewSuggestion
from .review_prompts import ReviewPrompts
from .severity_classifier import SeverityClassifier


class CodeReviewAgent(BaseEnterpriseAgent):
    """Agent for automated code review using configured LLM.
    
    Uses agent's configured LLM provider (any of 8).
    Provides expert-level code review with structured output.
    
    Capabilities:
        - File-level code review
        - PR review with multiple files
        - Best practices checking
        - Improvement suggestions
    
    Attributes:
        severity_classifier: Classifier for finding severity
        prompts: Prompt templates for review
    """
    
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.CODE_REVIEW
    AGENT_CATEGORY: ClassVar[str] = "code_review"
    
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = """You are an expert code reviewer with deep knowledge of:
1. Clean code principles and SOLID design
2. Security best practices and common vulnerabilities
3. Performance optimization patterns
4. Language-specific idioms and conventions
5. Testing and maintainability

Provide constructive, actionable feedback that helps developers improve.
Be specific about issues and always suggest improvements.
Prioritize critical issues over style preferences."""
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize the code review agent."""
        super().__init__(config, llm_router)
        
        # Add code review capability
        self.add_capability(AgentCapability.CODE_REVIEW)
        
        # Initialize components
        self.severity_classifier = SeverityClassifier()
        self.prompts = ReviewPrompts()
    
    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Expert code review agent that analyzes code for quality, "
            "security, performance, and best practices. Uses configured "
            "LLM provider for intelligent analysis."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code review based on context.
        
        Args:
            context: Must contain 'file_path' and 'content' or 'pr_data'
            
        Returns:
            Review results with findings and suggestions
        """
        if "pr_data" in context:
            results = await self.review_pr(context["pr_data"])
            return {
                "status": "success",
                "review_type": "pr",
                "results": [self._result_to_dict(r) for r in results],
            }
        elif "file_path" in context and "content" in context:
            result = await self.review_file(
                file_path=context["file_path"],
                content=context["content"],
                diff=context.get("diff"),
            )
            return {
                "status": "success",
                "review_type": "file",
                "result": self._result_to_dict(result),
            }
        else:
            return {
                "status": "error",
                "message": "Context must contain 'pr_data' or 'file_path' and 'content'",
            }
    
    async def review_file(
        self,
        file_path: str,
        content: str,
        diff: Optional[str] = None,
        language: Optional[str] = None,
    ) -> CodeReviewResult:
        """Review a single file using configured LLM.
        
        The LLM provider is determined by agent's llm_config.
        
        Args:
            file_path: Path to the file being reviewed
            content: File content to review
            diff: Optional diff showing changes
            language: Optional language override
            
        Returns:
            Structured code review result
        """
        # Detect language if not provided
        if not language:
            language = self._detect_language(file_path)
        
        # Build the review prompt
        prompt = self.prompts.build_file_review_prompt(
            file_path=file_path,
            content=content,
            diff=diff,
            language=language,
        )
        
        # Get LLM response
        response = await self.complete(prompt)
        
        # Parse and return structured result
        return self._parse_review_response(file_path, response)
    
    async def review_pr(
        self,
        pr_data: Dict[str, Any],
    ) -> List[CodeReviewResult]:
        """Review a pull request with multiple files.
        
        Args:
            pr_data: PR data including files, diffs, and metadata
            
        Returns:
            List of review results, one per file
        """
        results: List[CodeReviewResult] = []
        
        files = pr_data.get("files", [])
        for file_info in files:
            file_path = file_info.get("path", "")
            content = file_info.get("content", "")
            diff = file_info.get("diff")
            
            if content:  # Skip deleted files
                result = await self.review_file(
                    file_path=file_path,
                    content=content,
                    diff=diff,
                )
                results.append(result)
        
        return results
    
    async def suggest_improvements(
        self,
        code: str,
        language: str,
    ) -> List[Suggestion]:
        """Suggest improvements for code.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            List of improvement suggestions
        """
        prompt = self.prompts.build_improvement_prompt(code, language)
        response = await self.complete(prompt)
        return self._parse_suggestions(response)
    
    async def check_best_practices(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:
        """Check code against best practices.
        
        Args:
            code: Code to check
            language: Programming language
            
        Returns:
            List of best practice violations found
        """
        prompt = self.prompts.build_best_practices_prompt(code, language)
        response = await self.complete(prompt)
        return self._parse_findings(response)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".cpp": "cpp",
            ".c": "c",
            ".swift": "swift",
            ".kt": "kotlin",
        }
        
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        
        return "unknown"
    
    def _parse_review_response(
        self,
        file_path: str,
        response: str,
    ) -> CodeReviewResult:
        """Parse LLM response into structured result."""
        findings: List[Finding] = []
        suggestions: List[Suggestion] = []
        severity_counts: Dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        
        # Try to parse JSON response
        try:
            data = json.loads(response)
            
            for f in data.get("findings", []):
                severity = self.severity_classifier.classify(
                    f.get("message", ""),
                    f.get("category", ""),
                )
                finding = Finding(
                    id=f.get("id", str(uuid.uuid4())),
                    severity=severity,
                    category=f.get("category", "general"),
                    message=f.get("message", ""),
                    line_start=f.get("line_start", 1),
                    line_end=f.get("line_end"),
                    suggestion=f.get("suggestion"),
                )
                findings.append(finding)
                severity_counts[severity.value] += 1
            
            for s in data.get("suggestions", []):
                suggestion = Suggestion(
                    id=s.get("id", str(uuid.uuid4())),
                    title=s.get("title", ""),
                    description=s.get("description", ""),
                    file_path=file_path,
                    line_start=s.get("line_start", 1),
                    line_end=s.get("line_end"),
                    original_code=s.get("original_code"),
                    suggested_code=s.get("suggested_code"),
                )
                suggestions.append(suggestion)
                
        except json.JSONDecodeError:
            # If not JSON, create a single finding from the response
            findings.append(Finding(
                id=str(uuid.uuid4()),
                severity=Severity.INFO,
                category="review",
                message=response[:500],
                line_start=1,
            ))
            severity_counts["info"] += 1
        
        # Calculate overall quality
        critical_weight = severity_counts["critical"] * 10
        high_weight = severity_counts["high"] * 5
        medium_weight = severity_counts["medium"] * 2
        low_weight = severity_counts["low"] * 1
        
        total_weight = critical_weight + high_weight + medium_weight + low_weight
        overall_quality = max(0.0, 1.0 - (total_weight / 100))
        
        # Determine approval status
        approved = (
            severity_counts["critical"] == 0 and
            severity_counts["high"] == 0
        )
        
        return CodeReviewResult(
            file_path=file_path,
            findings=findings,
            suggestions=suggestions,
            severity_counts=severity_counts,
            overall_quality=overall_quality,
            approved=approved,
            reviewer_id=self.id,
        )
    
    def _parse_suggestions(self, response: str) -> List[Suggestion]:
        """Parse suggestions from LLM response."""
        suggestions: List[Suggestion] = []
        
        try:
            data = json.loads(response)
            for s in data.get("suggestions", []):
                suggestions.append(Suggestion(
                    id=s.get("id", str(uuid.uuid4())),
                    title=s.get("title", ""),
                    description=s.get("description", ""),
                    file_path=s.get("file_path", ""),
                    line_start=s.get("line_start", 1),
                    original_code=s.get("original_code"),
                    suggested_code=s.get("suggested_code"),
                ))
        except json.JSONDecodeError:
            pass
        
        return suggestions
    
    def _parse_findings(self, response: str) -> List[Finding]:
        """Parse findings from LLM response."""
        findings: List[Finding] = []
        
        try:
            data = json.loads(response)
            for f in data.get("findings", []):
                severity = self.severity_classifier.classify(
                    f.get("message", ""),
                    f.get("category", ""),
                )
                findings.append(Finding(
                    id=f.get("id", str(uuid.uuid4())),
                    severity=severity,
                    category=f.get("category", "best_practice"),
                    message=f.get("message", ""),
                    line_start=f.get("line_start", 1),
                    suggestion=f.get("suggestion"),
                ))
        except json.JSONDecodeError:
            pass
        
        return findings
    
    def _result_to_dict(self, result: CodeReviewResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "file_path": result.file_path,
            "findings_count": len(result.findings),
            "suggestions_count": len(result.suggestions),
            "severity_counts": result.severity_counts,
            "overall_quality": result.overall_quality,
            "approved": result.approved,
            "reviewer_id": result.reviewer_id,
        }
