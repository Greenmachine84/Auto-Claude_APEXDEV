"""Architecture extractor for project analysis.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import re


@dataclass
class ArchitectureMap:
    """Architecture map of a project."""
    patterns: List[str] = field(default_factory=list)
    layers: List[str] = field(default_factory=list)
    modules: Dict[str, List[str]] = field(default_factory=dict)  # module -> files
    entry_points: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    abstractions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "patterns": self.patterns,
            "layers": self.layers,
            "modules": self.modules,
            "entry_points": self.entry_points,
            "interfaces": self.interfaces,
            "abstractions": self.abstractions,
        }


class ArchitectureExtractor:
    """Extracts architecture patterns from code.
    
    Analyzes project structure and code to identify
    architectural patterns and organization.
    """
    
    # Common layer names
    LAYER_PATTERNS = {
        "presentation": ["views", "templates", "pages", "components", "ui"],
        "application": ["services", "use_cases", "handlers", "controllers"],
        "domain": ["models", "entities", "domain", "core"],
        "infrastructure": ["repositories", "adapters", "database", "external"],
        "api": ["api", "routes", "endpoints", "rest"],
    }
    
    # Architecture pattern indicators
    PATTERN_INDICATORS = {
        "mvc": {
            "folders": ["models", "views", "controllers"],
            "files": ["*_controller.*", "*_view.*", "*_model.*"],
        },
        "clean_architecture": {
            "folders": ["entities", "use_cases", "adapters", "frameworks"],
            "files": ["*_usecase.*", "*_repository.*", "*_presenter.*"],
        },
        "hexagonal": {
            "folders": ["ports", "adapters", "domain", "application"],
            "files": ["*_port.*", "*_adapter.*"],
        },
        "layered": {
            "folders": ["presentation", "business", "data", "persistence"],
            "files": [],
        },
        "microservices": {
            "folders": ["services", "gateway", "common"],
            "files": ["docker-compose.*", "*_service.*"],
        },
        "monolithic": {
            "folders": ["app", "src", "lib"],
            "files": [],
        },
    }
    
    def __init__(self):
        """Initialize extractor."""
        self._patterns: List[str] = []
    
    def extract(
        self,
        files: Dict[str, str],
    ) -> ArchitectureMap:
        """Extract architecture from files.
        
        Args:
            files: Map of file paths to contents
            
        Returns:
            Architecture map
        """
        arch_map = ArchitectureMap()
        
        file_paths = list(files.keys())
        
        # Detect patterns
        arch_map.patterns = self._detect_patterns(file_paths)
        
        # Detect layers
        arch_map.layers = self._detect_layers(file_paths)
        
        # Group files into modules
        arch_map.modules = self._group_modules(file_paths)
        
        # Find entry points
        arch_map.entry_points = self._find_entry_points(files)
        
        # Find interfaces/abstractions
        arch_map.interfaces, arch_map.abstractions = self._find_abstractions(files)
        
        return arch_map
    
    def _detect_patterns(
        self,
        file_paths: List[str],
    ) -> List[str]:
        """Detect architecture patterns from file paths."""
        detected: List[str] = []
        
        # Extract folder names
        folders: Set[str] = set()
        for path in file_paths:
            parts = path.replace("\\", "/").split("/")
            folders.update(parts[:-1])  # Exclude filename
        
        folder_lower = {f.lower() for f in folders}
        
        # Check each pattern
        for pattern, indicators in self.PATTERN_INDICATORS.items():
            pattern_folders = set(indicators["folders"])
            matches = folder_lower & pattern_folders
            
            if len(matches) >= 2:  # At least 2 folder matches
                detected.append(pattern)
        
        # Check file patterns
        file_names = [p.split("/")[-1] for p in file_paths]
        
        for pattern, indicators in self.PATTERN_INDICATORS.items():
            if pattern in detected:
                continue
            
            for file_pattern in indicators["files"]:
                regex = file_pattern.replace("*", ".*").replace(".", "\\.")
                for file_name in file_names:
                    if re.match(regex, file_name, re.IGNORECASE):
                        if pattern not in detected:
                            detected.append(pattern)
                        break
        
        return detected if detected else ["monolithic"]
    
    def _detect_layers(
        self,
        file_paths: List[str],
    ) -> List[str]:
        """Detect architectural layers."""
        layers: List[str] = []
        
        folders: Set[str] = set()
        for path in file_paths:
            parts = path.replace("\\", "/").split("/")
            folders.update(p.lower() for p in parts[:-1])
        
        for layer, indicators in self.LAYER_PATTERNS.items():
            if any(ind in folders for ind in indicators):
                layers.append(layer)
        
        return layers
    
    def _group_modules(
        self,
        file_paths: List[str],
    ) -> Dict[str, List[str]]:
        """Group files into modules."""
        modules: Dict[str, List[str]] = {}
        
        for path in file_paths:
            parts = path.replace("\\", "/").split("/")
            
            # Use first-level directory as module
            if len(parts) >= 2:
                module = parts[0]
                if module not in modules:
                    modules[module] = []
                modules[module].append(path)
            else:
                if "root" not in modules:
                    modules["root"] = []
                modules["root"].append(path)
        
        return modules
    
    def _find_entry_points(
        self,
        files: Dict[str, str],
    ) -> List[str]:
        """Find application entry points."""
        entry_points: List[str] = []
        
        entry_indicators = [
            "main.py", "app.py", "__main__.py", "index.py",
            "main.js", "index.js", "app.js", "server.js",
            "main.ts", "index.ts", "app.ts", "server.ts",
        ]
        
        for path in files:
            file_name = path.split("/")[-1]
            if file_name in entry_indicators:
                entry_points.append(path)
        
        # Also check for if __name__ == "__main__" patterns
        for path, content in files.items():
            if path.endswith(".py"):
                if 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content:
                    if path not in entry_points:
                        entry_points.append(path)
        
        return entry_points
    
    def _find_abstractions(
        self,
        files: Dict[str, str],
    ) -> tuple[List[str], List[str]]:
        """Find interfaces and abstract classes."""
        interfaces: List[str] = []
        abstractions: List[str] = []
        
        for path, content in files.items():
            if path.endswith(".py"):
                # Python ABC
                if "ABC" in content or "abstractmethod" in content:
                    abstractions.append(path)
                # Python Protocol
                if "Protocol" in content:
                    interfaces.append(path)
            
            elif path.endswith(".ts"):
                # TypeScript interface
                if re.search(r"\binterface\s+\w+", content):
                    interfaces.append(path)
                # TypeScript abstract
                if re.search(r"\babstract\s+class\s+\w+", content):
                    abstractions.append(path)
            
            elif path.endswith(".java"):
                if re.search(r"\binterface\s+\w+", content):
                    interfaces.append(path)
                if re.search(r"\babstract\s+class\s+\w+", content):
                    abstractions.append(path)
        
        return interfaces, abstractions
    
    def get_architecture_summary(
        self,
        arch_map: ArchitectureMap,
    ) -> str:
        """Generate architecture summary."""
        lines = [
            "## Architecture Summary",
            "",
            f"**Detected Patterns:** {', '.join(arch_map.patterns) or 'None'}",
            f"**Layers:** {', '.join(arch_map.layers) or 'None'}",
            f"**Modules:** {len(arch_map.modules)}",
            f"**Entry Points:** {len(arch_map.entry_points)}",
            f"**Interfaces:** {len(arch_map.interfaces)}",
            f"**Abstract Classes:** {len(arch_map.abstractions)}",
        ]
        
        return "\n".join(lines)
