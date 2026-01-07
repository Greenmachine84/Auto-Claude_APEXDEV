"""API documentation generator for documentation agent.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import ast
import re


@dataclass
class APIEndpoint:
    """An API endpoint."""
    path: str
    method: str = "GET"
    summary: str = ""
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown documentation."""
        lines = [
            f"### `{self.method}` {self.path}",
            "",
            self.description or self.summary,
            "",
        ]
        
        if self.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            lines.append("| Name | Type | Required | Description |")
            lines.append("|------|------|----------|-------------|")
            for param in self.parameters:
                required = "✓" if param.get("required") else ""
                lines.append(
                    f"| {param.get('name', '')} | "
                    f"{param.get('type', 'string')} | "
                    f"{required} | "
                    f"{param.get('description', '')} |"
                )
            lines.append("")
        
        if self.request_body:
            lines.append("**Request Body:**")
            lines.append("")
            lines.append("```json")
            import json
            lines.append(json.dumps(self.request_body, indent=2))
            lines.append("```")
            lines.append("")
        
        if self.responses:
            lines.append("**Responses:**")
            lines.append("")
            for status, response in self.responses.items():
                lines.append(f"- **{status}**: {response.get('description', '')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI specification format."""
        spec: Dict[str, Any] = {
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags,
            "responses": {},
        }
        
        if self.parameters:
            spec["parameters"] = [
                {
                    "name": p.get("name"),
                    "in": p.get("in", "query"),
                    "required": p.get("required", False),
                    "schema": {"type": p.get("type", "string")},
                    "description": p.get("description", ""),
                }
                for p in self.parameters
            ]
        
        if self.request_body:
            spec["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": self.request_body,
                    }
                }
            }
        
        for status, response in self.responses.items():
            spec["responses"][status] = {
                "description": response.get("description", ""),
            }
        
        return spec


class APIDocGenerator:
    """Generates API documentation from code.
    
    Parses route definitions and generates documentation
    in markdown or OpenAPI format.
    """
    
    # Framework-specific route patterns
    ROUTE_PATTERNS = {
        "fastapi": [
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']',
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']',
        ],
        "flask": [
            r'@app\.route\(["\']([^"\']*)["\'](.*?)\)',
            r'@blueprint\.route\(["\']([^"\']*)["\'](.*?)\)',
        ],
        "express": [
            r'app\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']',
            r'router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']',
        ],
    }
    
    def __init__(self):
        """Initialize generator."""
        self._endpoints: List[APIEndpoint] = []
    
    def parse_fastapi(
        self,
        code: str,
    ) -> List[APIEndpoint]:
        """Parse FastAPI routes from code.
        
        Args:
            code: FastAPI application code
            
        Returns:
            List of parsed endpoints
        """
        endpoints: List[APIEndpoint] = []
        
        # Match FastAPI decorators
        pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\'].*?\)\s*(?:async\s+)?def\s+(\w+)'
        
        matches = re.finditer(pattern, code, re.DOTALL)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            func_name = match.group(3)
            
            # Try to find the function and its docstring
            func_pattern = rf'def {func_name}\([^)]*\)[^:]*:(?:\s*"""([^"]+)""")?'
            func_match = re.search(func_pattern, code)
            
            description = ""
            if func_match and func_match.group(1):
                description = func_match.group(1).strip()
            
            endpoints.append(APIEndpoint(
                path=path,
                method=method,
                summary=func_name.replace("_", " ").title(),
                description=description,
            ))
        
        return endpoints
    
    def parse_flask(
        self,
        code: str,
    ) -> List[APIEndpoint]:
        """Parse Flask routes from code.
        
        Args:
            code: Flask application code
            
        Returns:
            List of parsed endpoints
        """
        endpoints: List[APIEndpoint] = []
        
        pattern = r'@(?:app|blueprint)\.route\(["\']([^"\']+)["\'](?:.*?methods=\[([^\]]+)\])?.*?\)\s*def\s+(\w+)'
        
        matches = re.finditer(pattern, code, re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            methods_str = match.group(2)
            func_name = match.group(3)
            
            methods = ["GET"]
            if methods_str:
                methods = [m.strip().strip("'\"") for m in methods_str.split(",")]
            
            for method in methods:
                endpoints.append(APIEndpoint(
                    path=path,
                    method=method.upper(),
                    summary=func_name.replace("_", " ").title(),
                ))
        
        return endpoints
    
    def parse_express(
        self,
        code: str,
    ) -> List[APIEndpoint]:
        """Parse Express.js routes from code.
        
        Args:
            code: Express application code
            
        Returns:
            List of parsed endpoints
        """
        endpoints: List[APIEndpoint] = []
        
        pattern = r'(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        
        matches = re.finditer(pattern, code)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append(APIEndpoint(
                path=path,
                method=method,
                summary=path.replace("/", " ").strip().title() or "Root",
            ))
        
        return endpoints
    
    def generate_markdown(
        self,
        endpoints: List[APIEndpoint],
        title: str = "API Reference",
    ) -> str:
        """Generate markdown API documentation.
        
        Args:
            endpoints: List of API endpoints
            title: Documentation title
            
        Returns:
            Markdown documentation
        """
        lines = [
            f"# {title}",
            "",
            f"This API provides {len(endpoints)} endpoints.",
            "",
            "## Endpoints",
            "",
        ]
        
        # Group by tag or path
        for endpoint in endpoints:
            lines.append(endpoint.to_markdown())
        
        return "\n".join(lines)
    
    def generate_openapi(
        self,
        endpoints: List[APIEndpoint],
        info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Generate OpenAPI specification.
        
        Args:
            endpoints: List of API endpoints
            info: API info (title, version, description)
            
        Returns:
            OpenAPI specification dict
        """
        spec: Dict[str, Any] = {
            "openapi": "3.0.3",
            "info": info or {
                "title": "API",
                "version": "1.0.0",
                "description": "API Documentation",
            },
            "paths": {},
        }
        
        for endpoint in endpoints:
            path = endpoint.path
            method = endpoint.method.lower()
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            spec["paths"][path][method] = endpoint.to_openapi()
        
        return spec
    
    def detect_framework(
        self,
        code: str,
    ) -> str:
        """Detect the API framework from code.
        
        Args:
            code: Source code
            
        Returns:
            Detected framework name
        """
        if "FastAPI" in code or "from fastapi" in code:
            return "fastapi"
        elif "Flask" in code or "from flask" in code:
            return "flask"
        elif "express" in code or "require('express')" in code:
            return "express"
        else:
            return "unknown"
    
    def parse_code(
        self,
        code: str,
        framework: Optional[str] = None,
    ) -> List[APIEndpoint]:
        """Parse code and extract API endpoints.
        
        Args:
            code: Source code
            framework: Framework name (auto-detected if not provided)
            
        Returns:
            List of parsed endpoints
        """
        if not framework:
            framework = self.detect_framework(code)
        
        if framework == "fastapi":
            return self.parse_fastapi(code)
        elif framework == "flask":
            return self.parse_flask(code)
        elif framework == "express":
            return self.parse_express(code)
        else:
            return []
