"""
Tool Discovery - Phase 8 Implementation.

Automatic tool discovery and registration.

World-Class Standards:
- Plugin architecture
- Auto-discovery
- Manifest support
- Version compatibility
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import importlib
import pkgutil
import json
import logging

from ..models import Tool, ToolCategory
from .tool_registry import ToolRegistry
from .tool_loader import ToolLoader
from .tool_validator import ToolValidator

logger = logging.getLogger(__name__)


class ToolDiscovery:
    """
    Automatic tool discovery system.
    
    Features:
    - Package scanning
    - Manifest loading
    - Version compatibility
    - Plugin support
    """
    
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        loader: Optional[ToolLoader] = None,
    ) -> None:
        """Initialize discovery system."""
        self.registry = registry or ToolRegistry()
        self.loader = loader or ToolLoader(self.registry)
        
        self._discovered: List[str] = []
        self._manifests: Dict[str, Dict[str, Any]] = {}
        
        logger.info("ToolDiscovery initialized")
    
    async def discover_all(
        self,
        search_paths: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Discover and register all available tools.
        
        Args:
            search_paths: Optional list of paths to search
            
        Returns:
            List of discovered tool names
        """
        discovered = []
        
        # Default search paths
        if not search_paths:
            search_paths = [
                "tools.builtin",
                "tools.filesystem",
                "tools.git",
                "tools.search",
                "tools.web",
            ]
        
        for path in search_paths:
            try:
                if Path(path).exists():
                    # Directory path
                    found = await self._discover_from_directory(path)
                else:
                    # Module path
                    found = await self._discover_from_package(path)
                discovered.extend(found)
            except Exception as e:
                logger.warning("Failed to discover from %s: %s", path, e)
        
        self._discovered = discovered
        logger.info("Discovered %d tools total", len(discovered))
        
        return discovered
    
    async def _discover_from_package(self, package_path: str) -> List[str]:
        """Discover tools from a Python package."""
        discovered = []
        
        try:
            package = importlib.import_module(package_path)
            
            # Check for manifest
            manifest_path = Path(package.__file__).parent / "manifest.json"
            if manifest_path.exists():
                discovered.extend(await self._load_from_manifest(manifest_path))
            else:
                # Scan all submodules
                if hasattr(package, "__path__"):
                    for importer, modname, ispkg in pkgutil.iter_modules(
                        package.__path__, prefix=f"{package_path}."
                    ):
                        if not ispkg:
                            try:
                                loaded = await self.loader.load_from_module(modname)
                                discovered.extend(loaded)
                            except Exception as e:
                                logger.debug("Skipping %s: %s", modname, e)
            
        except ImportError as e:
            logger.debug("Package not found: %s (%s)", package_path, e)
        
        return discovered
    
    async def _discover_from_directory(self, directory: str) -> List[str]:
        """Discover tools from a directory."""
        discovered = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return discovered
        
        # Check for manifest
        manifest_path = dir_path / "manifest.json"
        if manifest_path.exists():
            return await self._load_from_manifest(manifest_path)
        
        # Scan Python files
        return await self.loader.load_from_directory(directory)
    
    async def _load_from_manifest(self, manifest_path: Path) -> List[str]:
        """Load tools defined in a manifest file."""
        discovered = []
        
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            self._manifests[str(manifest_path)] = manifest
            
            # Validate manifest version
            version = manifest.get("version", "1.0")
            if not self._check_version_compatibility(version):
                logger.warning(
                    "Manifest version %s may not be compatible", version
                )
            
            # Load tools from manifest
            tools = manifest.get("tools", [])
            for tool_def in tools:
                module_path = tool_def.get("module")
                if module_path:
                    try:
                        loaded = await self.loader.load_from_module(module_path)
                        discovered.extend(loaded)
                    except Exception as e:
                        logger.warning(
                            "Failed to load tool from %s: %s", module_path, e
                        )
            
        except json.JSONDecodeError as e:
            logger.error("Invalid manifest JSON: %s", e)
        except Exception as e:
            logger.error("Failed to load manifest: %s", e)
        
        return discovered
    
    def _check_version_compatibility(self, version: str) -> bool:
        """Check if manifest version is compatible."""
        # Simple version check
        major = int(version.split(".")[0])
        return major == 1  # Only version 1.x is supported
    
    async def discover_builtin(self) -> List[str]:
        """Discover builtin tools only."""
        return await self._discover_from_package("tools.builtin")
    
    async def discover_from_config(
        self,
        config: Dict[str, Any],
    ) -> List[str]:
        """Discover tools based on configuration."""
        discovered = []
        
        # Load enabled tool packages
        packages = config.get("tool_packages", [])
        for package in packages:
            if package.get("enabled", True):
                path = package.get("path")
                if path:
                    found = await self._discover_from_package(path)
                    discovered.extend(found)
        
        # Load custom tool directories
        custom_dirs = config.get("custom_tool_directories", [])
        for directory in custom_dirs:
            found = await self._discover_from_directory(directory)
            discovered.extend(found)
        
        return discovered
    
    def get_discovered(self) -> List[str]:
        """Get list of discovered tool names."""
        return self._discovered.copy()
    
    def get_manifest(self, path: str) -> Optional[Dict[str, Any]]:
        """Get loaded manifest by path."""
        return self._manifests.get(path)
    
    async def refresh(self) -> List[str]:
        """Re-discover all tools."""
        return await self.discover_all()
