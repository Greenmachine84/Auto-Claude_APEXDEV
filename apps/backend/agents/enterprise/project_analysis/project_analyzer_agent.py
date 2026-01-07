"""Project Analyzer Agent for codebase analysis.

World-Class Standards:
- Comprehensive dependency mapping
- Architecture extraction
- Technical debt analysis
- LLM-agnostic design

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from typing import Any, ClassVar, Dict, List, Optional
import json

from ..base_enterprise_agent import BaseEnterpriseAgent, LLMRouter
from ..config import AgentCapability, EnterpriseAgentConfig
from ..types import EnterpriseAgentType
from .dependency_mapper import DependencyMapper, DependencyGraph
from .architecture_extractor import ArchitectureExtractor, ArchitectureMap
from .tech_debt_analyzer import TechDebtAnalyzer, TechDebtReport


class ProjectAnalyzerAgent(BaseEnterpriseAgent):
    """Agent for comprehensive project analysis.
    
    Provides project analysis capabilities:
    - Dependency mapping and visualization
    - Architecture pattern detection
    - Technical debt assessment
    - Codebase health metrics
    
    Attributes:
        dependency_mapper: Dependency analysis utility
        architecture_extractor: Architecture pattern detector
        tech_debt_analyzer: Technical debt analyzer
    """
    
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.PROJECT_ANALYSIS
    AGENT_CATEGORY: ClassVar[str] = "project_analysis"
    
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = """You are an expert software architect with deep knowledge of:
1. Software architecture patterns (MVC, Clean, Hexagonal, etc.)
2. Dependency management and module design
3. Technical debt identification and remediation
4. Code quality metrics and best practices
5. Project structure and organization

Analyze projects thoroughly and provide actionable insights.
Identify patterns and anti-patterns.
Suggest improvements based on industry best practices."""
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize the project analyzer agent."""
        super().__init__(config, llm_router)
        
        # Add analysis capability
        self.add_capability(AgentCapability.CODE_ANALYSIS)
        
        # Initialize components
        self.dependency_mapper = DependencyMapper()
        self.architecture_extractor = ArchitectureExtractor()
        self.tech_debt_analyzer = TechDebtAnalyzer()
    
    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Project analyzer that maps dependencies, extracts architecture "
            "patterns, and identifies technical debt. Provides comprehensive "
            "insights for codebase improvement."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project analysis based on context.
        
        Args:
            context: Must contain 'files' or 'project_path'
            
        Returns:
            Project analysis results
        """
        files = context.get("files", {})
        analysis_type = context.get("analysis_type", "full")
        
        if not files:
            return {
                "status": "error",
                "message": "Context must contain 'files' dictionary",
            }
        
        results: Dict[str, Any] = {"status": "success"}
        
        if analysis_type in ("full", "dependencies"):
            results["dependencies"] = self.analyze_dependencies(files)
        
        if analysis_type in ("full", "architecture"):
            results["architecture"] = await self.analyze_architecture(files)
        
        if analysis_type in ("full", "tech_debt"):
            results["tech_debt"] = await self.analyze_tech_debt(files)
        
        return results
    
    def analyze_dependencies(
        self,
        files: Dict[str, str],
    ) -> Dict[str, Any]:
        """Analyze project dependencies.
        
        Args:
            files: Map of file paths to contents
            
        Returns:
            Dependency analysis results
        """
        graph = self.dependency_mapper.build_graph(files)
        
        return {
            "total_files": len(graph.nodes),
            "total_dependencies": len(graph.edges),
            "external_dependencies": graph.external_deps,
            "internal_dependencies": graph.internal_deps,
            "circular_dependencies": graph.circular_deps,
            "orphan_files": graph.orphan_files,
            "hub_files": graph.hub_files,  # Files with many dependencies
        }
    
    async def analyze_architecture(
        self,
        files: Dict[str, str],
    ) -> Dict[str, Any]:
        """Analyze project architecture.
        
        Args:
            files: Map of file paths to contents
            
        Returns:
            Architecture analysis results
        """
        # Initial static analysis
        arch_map = self.architecture_extractor.extract(files)
        
        # LLM-enhanced analysis
        prompt = f"""Analyze this project architecture.

Project Structure:
{json.dumps(arch_map.to_dict(), indent=2)}

Identify:
1. Primary architecture pattern (MVC, Clean Architecture, etc.)
2. Layer organization
3. Module coupling assessment
4. Adherence to SOLID principles
5. Suggestions for improvement

Provide analysis in JSON format:
{{
  "primary_pattern": "Pattern name",
  "confidence": 0.0-1.0,
  "layers": ["layer1", "layer2"],
  "coupling_score": "low|medium|high",
  "solid_assessment": {{
    "single_responsibility": "assessment",
    "open_closed": "assessment",
    "liskov_substitution": "assessment",
    "interface_segregation": "assessment",
    "dependency_inversion": "assessment"
  }},
  "improvements": ["suggestion1", "suggestion2"]
}}
"""
        
        response = await self.complete(prompt)
        
        try:
            llm_analysis = json.loads(response)
            return {
                "detected_patterns": arch_map.patterns,
                "layers": arch_map.layers,
                "modules": arch_map.modules,
                "llm_analysis": llm_analysis,
            }
        except json.JSONDecodeError:
            return {
                "detected_patterns": arch_map.patterns,
                "layers": arch_map.layers,
                "modules": arch_map.modules,
                "raw_analysis": response,
            }
    
    async def analyze_tech_debt(
        self,
        files: Dict[str, str],
    ) -> Dict[str, Any]:
        """Analyze technical debt.
        
        Args:
            files: Map of file paths to contents
            
        Returns:
            Technical debt analysis
        """
        # Static analysis
        report = self.tech_debt_analyzer.analyze(files)
        
        # LLM-enhanced prioritization
        if report.items:
            prompt = f"""Prioritize these technical debt items.

Items:
{json.dumps([item.to_dict() for item in report.items[:20]], indent=2)}

Provide prioritized list in JSON format:
{{
  "prioritized_items": [
    {{
      "item": "description",
      "priority": "critical|high|medium|low",
      "effort": "small|medium|large",
      "impact": "high|medium|low",
      "recommendation": "what to do"
    }}
  ],
  "summary": "Overall tech debt assessment",
  "quick_wins": ["Low effort, high impact items"]
}}
"""
            
            response = await self.complete(prompt)
            
            try:
                llm_prioritization = json.loads(response)
                return {
                    "total_items": len(report.items),
                    "total_score": report.total_score,
                    "by_category": report.by_category,
                    "prioritized": llm_prioritization,
                }
            except json.JSONDecodeError:
                pass
        
        return {
            "total_items": len(report.items),
            "total_score": report.total_score,
            "by_category": report.by_category,
            "items": [item.to_dict() for item in report.items],
        }
    
    async def generate_project_summary(
        self,
        files: Dict[str, str],
    ) -> str:
        """Generate a comprehensive project summary.
        
        Args:
            files: Map of file paths to contents
            
        Returns:
            Project summary markdown
        """
        # Gather all analyses
        deps = self.analyze_dependencies(files)
        arch_map = self.architecture_extractor.extract(files)
        tech_debt = self.tech_debt_analyzer.analyze(files)
        
        prompt = f"""Generate a comprehensive project summary.

Project Statistics:
- Files: {deps['total_files']}
- Dependencies: {deps['total_dependencies']}
- Circular Dependencies: {len(deps['circular_dependencies'])}

Architecture:
- Patterns: {arch_map.patterns}
- Layers: {arch_map.layers}
- Modules: {len(arch_map.modules)}

Technical Debt:
- Total Items: {len(tech_debt.items)}
- Score: {tech_debt.total_score}

Generate a markdown summary including:
1. Project Overview
2. Architecture Assessment
3. Code Quality Metrics
4. Technical Debt Summary
5. Recommendations
6. Priority Actions
"""
        
        return await self.complete(prompt)
    
    async def suggest_refactoring(
        self,
        code: str,
        context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest refactoring opportunities.
        
        Args:
            code: Code to analyze
            context: Optional context about the codebase
            
        Returns:
            List of refactoring suggestions
        """
        prompt = f"""Analyze this code for refactoring opportunities.

{f"Context: {context}" if context else ""}

Code:
```
{code}
```

Provide refactoring suggestions in JSON format:
{{
  "suggestions": [
    {{
      "type": "extract_method|rename|move|inline|...",
      "location": "line or function name",
      "current": "current code/structure",
      "suggested": "suggested change",
      "rationale": "why this improves the code",
      "effort": "low|medium|high"
    }}
  ]
}}

Focus on:
- DRY violations
- Long methods
- Complex conditionals
- Poor naming
- Missing abstractions
"""
        
        response = await self.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("suggestions", [])
        except json.JSONDecodeError:
            return [{"raw_suggestion": response}]
