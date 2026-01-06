"""Dependency analysis skill.

Analyzes project dependencies.

Capabilities:
- Map dependencies
- Detect circular deps
- Identify outdated deps
- Security vulnerability check
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


class DependencyType(Enum):
    """Types of dependencies."""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"
    PEER = "peer"


@dataclass
class Dependency:
    """A project dependency."""
    name: str
    version: str
    dep_type: DependencyType
    latest_version: Optional[str] = None
    is_outdated: bool = False
    vulnerabilities: List[str] = field(default_factory=list)
    transitive_deps: List[str] = field(default_factory=list)


@dataclass
class DependencyGraph:
    """Dependency relationship graph."""
    nodes: List[str]
    edges: List[tuple]
    circular_deps: List[List[str]] = field(default_factory=list)


class DependencyAnalysisSkill(BaseSkill):
    """Analyze project dependencies.
    
    Maps dependencies, detects circular dependencies,
    and identifies outdated or vulnerable packages.
    
    Example:
        skill = DependencyAnalysisSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "manifest_file": "requirements.txt",
                "check_vulnerabilities": True,
            }
        )
        result = await skill.run(context)
    """
    
    name = "dependency_analysis"
    description = "Analyze project dependencies"
    category = SkillCategory.ANALYSIS
    required_tools = ["file_read", "command_execute"]
    required_permissions = {"read_files", "execute_commands"}
    version = "1.0.0"
    
    # Supported manifest files
    MANIFEST_FILES = {
        "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
        "javascript": ["package.json", "package-lock.json", "yarn.lock"],
        "go": ["go.mod", "go.sum"],
        "rust": ["Cargo.toml", "Cargo.lock"],
    }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return True  # Will auto-detect if no manifest specified
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute dependency analysis.
        
        Args:
            context: Execution context with manifest
            
        Returns:
            SkillResult with dependency report
        """
        input_data = context.input_data
        manifest_file = input_data.get("manifest_file")
        check_vulnerabilities = input_data.get("check_vulnerabilities", False)
        check_outdated = input_data.get("check_outdated", False)
        
        # Parse dependencies
        deps = self._parse_dependencies(manifest_file)
        
        # Build dependency graph
        graph = self._build_graph(deps)
        
        # Check for issues
        if check_vulnerabilities:
            deps = self._check_vulnerabilities(deps)
        if check_outdated:
            deps = self._check_outdated(deps)
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "dependencies": [self._dep_to_dict(d) for d in deps],
                "total_count": len(deps),
                "outdated_count": sum(1 for d in deps if d.is_outdated),
                "vulnerable_count": sum(1 for d in deps if d.vulnerabilities),
                "circular_deps": graph.circular_deps,
            },
            tokens_used=0,
        )
    
    def _parse_dependencies(self, manifest_file: Optional[str]) -> List[Dependency]:
        """Parse dependencies from manifest."""
        # Placeholder
        return []
    
    def _build_graph(self, deps: List[Dependency]) -> DependencyGraph:
        """Build dependency graph."""
        nodes = [d.name for d in deps]
        edges = []
        for dep in deps:
            for trans in dep.transitive_deps:
                edges.append((dep.name, trans))
        
        circular = self._detect_circular(nodes, edges)
        
        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            circular_deps=circular,
        )
    
    def _detect_circular(self, nodes: List[str], edges: List[tuple]) -> List[List[str]]:
        """Detect circular dependencies."""
        # Placeholder - will use graph algorithms
        return []
    
    def _check_vulnerabilities(self, deps: List[Dependency]) -> List[Dependency]:
        """Check dependencies for vulnerabilities."""
        # Placeholder - will check vulnerability databases
        return deps
    
    def _check_outdated(self, deps: List[Dependency]) -> List[Dependency]:
        """Check for outdated dependencies."""
        # Placeholder - will check package registries
        return deps
    
    def _dep_to_dict(self, dep: Dependency) -> Dict[str, Any]:
        """Convert Dependency to dictionary."""
        return {
            "name": dep.name,
            "version": dep.version,
            "type": dep.dep_type.value,
            "latest_version": dep.latest_version,
            "is_outdated": dep.is_outdated,
            "vulnerabilities": dep.vulnerabilities,
        }
