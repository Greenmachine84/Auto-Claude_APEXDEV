"""
Agent Documentation Generator - Phase 10 Implementation.

World-Class Standards:
- Agent capability documentation
- Per-agent LLM configuration docs
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Agent configuration documentation."""
    name: str
    description: str = ""
    llm_provider: Optional[str] = None
    model: Optional[str] = None
    capabilities: List[AgentCapability] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    system_prompt: str = ""


class AgentDocGenerator:
    """Generate agent documentation."""

    # All 8 LLM providers
    SUPPORTED_PROVIDERS = {
        "copilot", "openrouter", "ollama", "lmstudio",
        "gemini", "openai", "anthropic", "azure"
    }

    def __init__(self):
        self.agents: List[AgentConfig] = []

    def add_agent(self, agent: AgentConfig) -> None:
        """Add agent configuration to documentation."""
        self.agents.append(agent)

    def validate_provider(self, provider: str) -> bool:
        """Validate provider is supported."""
        return provider in self.SUPPORTED_PROVIDERS

    def generate_markdown(self) -> str:
        """Generate Markdown documentation for all agents."""
        lines = [
            "# Agent Documentation",
            "",
            "Auto-Claude APEX Development agent configurations.",
            "",
            "## Supported LLM Providers",
            "",
            "All agents support the following 8 LLM providers (no default):",
            "",
        ]

        for provider in sorted(self.SUPPORTED_PROVIDERS):
            lines.append(f"- `{provider}`")
        lines.append("")

        for agent in self.agents:
            lines.append(f"## {agent.name}")
            lines.append("")
            if agent.description:
                lines.append(agent.description)
                lines.append("")

            lines.append("### Configuration")
            lines.append("")
            lines.append("| Setting | Value |")
            lines.append("|---------|-------|")

            if agent.llm_provider:
                lines.append(f"| LLM Provider | `{agent.llm_provider}` |")
            if agent.model:
                lines.append(f"| Model | `{agent.model}` |")
            lines.append("")

            if agent.capabilities:
                lines.append("### Capabilities")
                lines.append("")
                for cap in agent.capabilities:
                    lines.append(f"#### {cap.name}")
                    lines.append("")
                    lines.append(cap.description)
                    lines.append("")
                    if cap.inputs:
                        lines.append("**Inputs:**")
                        for input_name in cap.inputs:
                            lines.append(f"- `{input_name}`")
                        lines.append("")
                    if cap.outputs:
                        lines.append("**Outputs:**")
                        for output_name in cap.outputs:
                            lines.append(f"- `{output_name}`")
                        lines.append("")

            if agent.tools:
                lines.append("### Tools")
                lines.append("")
                for tool in agent.tools:
                    lines.append(f"- `{tool}`")
                lines.append("")

        return "\n".join(lines)

    def generate_config_template(self, agent: AgentConfig) -> Dict[str, Any]:
        """Generate configuration template for agent."""
        return {
            "name": agent.name,
            "description": agent.description,
            "llm": {
                "provider": agent.llm_provider or "<provider>",
                "model": agent.model or "<model>",
            },
            "tools": agent.tools,
            "capabilities": [
                {
                    "name": cap.name,
                    "inputs": cap.inputs,
                    "outputs": cap.outputs,
                }
                for cap in agent.capabilities
            ],
        }

    def export_markdown(self, filepath: str) -> None:
        """Export agent documentation as Markdown."""
        content = self.generate_markdown()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def export_config_templates(self, directory: str) -> List[str]:
        """Export configuration templates for all agents."""
        import os
        import json
        os.makedirs(directory, exist_ok=True)

        exported = []
        for agent in self.agents:
            filepath = os.path.join(directory, f"{agent.name.lower()}_config.json")
            template = self.generate_config_template(agent)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2)
            exported.append(filepath)

        return exported
