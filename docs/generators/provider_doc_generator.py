"""
Provider Documentation Generator - Phase 10 Implementation.

World-Class Standards:
- All 8 LLM providers documented
- Configuration and capabilities
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """Provider configuration."""
    id: str
    name: str
    type: str  # "cloud" or "local"
    description: str = ""
    auth_required: bool = True
    base_url: Optional[str] = None
    models: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    cost_per_1k_tokens: Dict[str, float] = field(default_factory=dict)


class ProviderDocGenerator:
    """Generate LLM provider documentation."""

    # All 8 LLM providers with configurations
    DEFAULT_PROVIDERS: List[ProviderConfig] = [
        ProviderConfig(
            id="copilot",
            name="GitHub Copilot",
            type="cloud",
            description="GitHub Copilot integration via VS Code.",
            auth_required=True,
            models=["gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet"],
            features=["code-completion", "chat", "inline-suggestions"],
            rate_limits={"rpm": 100, "tpm": 50000},
            cost_per_1k_tokens={"input": 0.0, "output": 0.0},  # Subscription
        ),
        ProviderConfig(
            id="openrouter",
            name="OpenRouter",
            type="cloud",
            description="Multi-model API aggregator with 100+ models.",
            auth_required=True,
            base_url="https://openrouter.ai/api/v1",
            models=["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "meta-llama/llama-3.1-70b"],
            features=["chat", "function-calling", "streaming"],
            rate_limits={"rpm": 100, "tpm": 100000},
            cost_per_1k_tokens={"input": 0.003, "output": 0.015},
        ),
        ProviderConfig(
            id="ollama",
            name="Ollama",
            type="local",
            description="Local LLM runner with broad model support.",
            auth_required=False,
            base_url="http://localhost:11434",
            models=["llama3.1", "mistral", "codellama", "qwen2.5-coder"],
            features=["chat", "embeddings", "streaming"],
            rate_limits={"rpm": 200, "tpm": None},
            cost_per_1k_tokens={"input": 0.0, "output": 0.0},
        ),
        ProviderConfig(
            id="lmstudio",
            name="LM Studio",
            type="local",
            description="Desktop application for local LLM inference.",
            auth_required=False,
            base_url="http://localhost:1234/v1",
            models=["local-model"],
            features=["chat", "embeddings", "openai-compatible"],
            rate_limits={"rpm": 200, "tpm": None},
            cost_per_1k_tokens={"input": 0.0, "output": 0.0},
        ),
        ProviderConfig(
            id="gemini",
            name="Google Gemini",
            type="cloud",
            description="Google's multimodal AI models.",
            auth_required=True,
            base_url="https://generativelanguage.googleapis.com/v1",
            models=["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            features=["chat", "multimodal", "function-calling", "streaming"],
            rate_limits={"rpm": 60, "tpm": 30000},
            cost_per_1k_tokens={"input": 0.00025, "output": 0.0005},
        ),
        ProviderConfig(
            id="openai",
            name="OpenAI",
            type="cloud",
            description="OpenAI's GPT models via API.",
            auth_required=True,
            base_url="https://api.openai.com/v1",
            models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o3-mini"],
            features=["chat", "function-calling", "streaming", "vision"],
            rate_limits={"rpm": 60, "tpm": 90000},
            cost_per_1k_tokens={"input": 0.005, "output": 0.015},
        ),
        ProviderConfig(
            id="anthropic",
            name="Anthropic",
            type="cloud",
            description="Anthropic's Claude models.",
            auth_required=True,
            base_url="https://api.anthropic.com/v1",
            models=["claude-3.5-sonnet-latest", "claude-3.5-haiku-latest", "claude-3-opus"],
            features=["chat", "function-calling", "streaming", "vision"],
            rate_limits={"rpm": 50, "tpm": 100000},
            cost_per_1k_tokens={"input": 0.003, "output": 0.015},
        ),
        ProviderConfig(
            id="azure",
            name="Azure OpenAI",
            type="cloud",
            description="Microsoft Azure-hosted OpenAI models.",
            auth_required=True,
            models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            features=["chat", "function-calling", "streaming", "vision"],
            rate_limits={"rpm": 100, "tpm": 120000},
            cost_per_1k_tokens={"input": 0.005, "output": 0.015},
        ),
    ]

    def __init__(self):
        self.providers = self.DEFAULT_PROVIDERS.copy()

    def add_provider(self, provider: ProviderConfig) -> None:
        """Add custom provider configuration."""
        self.providers.append(provider)

    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider by ID."""
        for provider in self.providers:
            if provider.id == provider_id:
                return provider
        return None

    def generate_markdown(self) -> str:
        """Generate Markdown documentation for all providers."""
        lines = [
            "# LLM Provider Documentation",
            "",
            "Auto-Claude APEX supports 8 LLM providers with no default.",
            "",
            "## Provider Overview",
            "",
            "| Provider | Type | Auth Required | Rate Limit (RPM) |",
            "|----------|------|---------------|------------------|",
        ]

        for p in self.providers:
            auth = "Yes" if p.auth_required else "No"
            rpm = p.rate_limits.get("rpm", "N/A")
            lines.append(f"| {p.name} | {p.type} | {auth} | {rpm} |")

        lines.append("")

        for provider in self.providers:
            lines.append(f"## {provider.name} (`{provider.id}`)")
            lines.append("")
            lines.append(provider.description)
            lines.append("")

            lines.append("### Configuration")
            lines.append("")
            lines.append("| Setting | Value |")
            lines.append("|---------|-------|")
            lines.append(f"| Type | {provider.type} |")
            lines.append(f"| Auth Required | {'Yes' if provider.auth_required else 'No'} |")
            if provider.base_url:
                lines.append(f"| Base URL | `{provider.base_url}` |")
            lines.append("")

            if provider.models:
                lines.append("### Supported Models")
                lines.append("")
                for model in provider.models:
                    lines.append(f"- `{model}`")
                lines.append("")

            if provider.features:
                lines.append("### Features")
                lines.append("")
                for feature in provider.features:
                    lines.append(f"- {feature}")
                lines.append("")

            if provider.rate_limits:
                lines.append("### Rate Limits")
                lines.append("")
                for key, value in provider.rate_limits.items():
                    if value is not None:
                        lines.append(f"- **{key.upper()}**: {value}")
                lines.append("")

            if provider.cost_per_1k_tokens:
                lines.append("### Pricing (per 1K tokens)")
                lines.append("")
                lines.append(f"- Input: ${provider.cost_per_1k_tokens.get('input', 0):.4f}")
                lines.append(f"- Output: ${provider.cost_per_1k_tokens.get('output', 0):.4f}")
                lines.append("")

        return "\n".join(lines)

    def export_markdown(self, filepath: str) -> None:
        """Export provider documentation as Markdown."""
        content = self.generate_markdown()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def generate_env_template(self) -> str:
        """Generate environment variable template."""
        lines = [
            "# Auto-Claude APEX LLM Provider Configuration",
            "# Configure ONLY the providers you need (no default)",
            "",
        ]

        for provider in self.providers:
            lines.append(f"# {provider.name}")
            if provider.auth_required:
                lines.append(f"# {provider.id.upper()}_API_KEY=your-api-key-here")
            if provider.base_url:
                lines.append(f"# {provider.id.upper()}_BASE_URL={provider.base_url}")
            lines.append("")

        return "\n".join(lines)

    def export_env_template(self, filepath: str) -> None:
        """Export .env template file."""
        content = self.generate_env_template()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
