"""Dynamic model selection based on task.

Part of Phase 2: LLM Architecture
"""

import logging
from dataclasses import dataclass
from enum import Enum

from .llm_config import LLMConfig, ModelConfig, TaskType

logger = logging.getLogger(__name__)


class SelectionCriteria(Enum):
    """Criteria for model selection."""

    QUALITY = "quality"  # Best quality, regardless of cost
    SPEED = "speed"  # Fastest response time
    COST = "cost"  # Lowest cost
    BALANCED = "balanced"  # Balance of all factors
    CAPABILITY = "capability"  # Specific capability required


@dataclass
class SelectionConstraints:
    """Constraints for model selection."""

    max_cost_per_1k: float | None = None
    max_latency_ms: float | None = None
    min_context_window: int | None = None
    requires_streaming: bool = False
    requires_tools: bool = False
    requires_vision: bool = False
    preferred_providers: list[str] | None = None
    excluded_providers: list[str] | None = None


@dataclass
class ModelScore:
    """Scored model for selection."""

    model: str
    provider: str
    score: float
    reasons: dict[str, float]


class ModelSelector:
    """Dynamic model selection based on task requirements.

    Selects the best model based on:
    - Task complexity
    - Cost constraints
    - Latency requirements
    - Required capabilities
    """

    def __init__(self, config: LLMConfig | None = None):
        self._config = config or LLMConfig()
        self._model_performance: dict[str, dict[str, float]] = {}  # model -> metrics

    def select(
        self,
        task_type: TaskType,
        criteria: SelectionCriteria = SelectionCriteria.BALANCED,
        constraints: SelectionConstraints | None = None,
    ) -> str | None:
        """Select the best model for the task."""
        constraints = constraints or SelectionConstraints()

        # Get all registered models
        candidates = self._get_candidates(constraints)
        if not candidates:
            # Fall back to default for task type
            return self._config.get_default_model(task_type)

        # Score each candidate
        scored = []
        for model_name in candidates:
            model = self._config.get_model(model_name)
            if model:
                score = self._score_model(model, task_type, criteria)
                scored.append(
                    ModelScore(
                        model=model_name,
                        provider=model.provider,
                        score=score["total"],
                        reasons=score,
                    )
                )

        if not scored:
            return self._config.get_default_model(task_type)

        # Sort by score and return best
        scored.sort(key=lambda x: x.score, reverse=True)
        logger.info("Selected model %s (score=%.2f)", scored[0].model, scored[0].score)
        return scored[0].model

    def select_with_fallbacks(
        self,
        task_type: TaskType,
        count: int = 3,
        criteria: SelectionCriteria = SelectionCriteria.BALANCED,
        constraints: SelectionConstraints | None = None,
    ) -> list[str]:
        """Select multiple models for fallback chain."""
        constraints = constraints or SelectionConstraints()
        candidates = self._get_candidates(constraints)

        scored = []
        for model_name in candidates:
            model = self._config.get_model(model_name)
            if model:
                score = self._score_model(model, task_type, criteria)
                scored.append((model_name, score["total"]))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored[:count]]

    def _get_candidates(self, constraints: SelectionConstraints) -> list[str]:
        """Get candidate models that meet constraints."""
        candidates = []

        for name, model in self._config._models.items():
            # Check capability constraints
            if constraints.requires_streaming and not model.supports_streaming:
                continue
            if constraints.requires_tools and not model.supports_tools:
                continue
            if constraints.requires_vision and not model.supports_vision:
                continue

            # Check context window
            if constraints.min_context_window:
                if model.context_window < constraints.min_context_window:
                    continue

            # Check cost
            if constraints.max_cost_per_1k:
                if model.cost_per_1k_input > constraints.max_cost_per_1k:
                    continue

            # Check provider preferences
            if constraints.preferred_providers:
                if model.provider not in constraints.preferred_providers:
                    continue
            if constraints.excluded_providers:
                if model.provider in constraints.excluded_providers:
                    continue

            candidates.append(name)

        return candidates

    def _score_model(
        self, model: ModelConfig, task_type: TaskType, criteria: SelectionCriteria
    ) -> dict[str, float]:
        """Score a model based on criteria."""
        scores = {
            "quality": self._score_quality(model, task_type),
            "speed": self._score_speed(model),
            "cost": self._score_cost(model),
            "capability": self._score_capability(model, task_type),
        }

        # Weight based on criteria
        if criteria == SelectionCriteria.QUALITY:
            weights = {"quality": 0.6, "speed": 0.1, "cost": 0.1, "capability": 0.2}
        elif criteria == SelectionCriteria.SPEED:
            weights = {"quality": 0.2, "speed": 0.5, "cost": 0.1, "capability": 0.2}
        elif criteria == SelectionCriteria.COST:
            weights = {"quality": 0.2, "speed": 0.1, "cost": 0.5, "capability": 0.2}
        else:  # BALANCED
            weights = {"quality": 0.3, "speed": 0.25, "cost": 0.2, "capability": 0.25}

        scores["total"] = sum(scores[k] * weights[k] for k in weights)
        return scores

    def _score_quality(self, model: ModelConfig, task_type: TaskType) -> float:
        """Score model quality for task type."""
        # Base quality on context window and provider reputation
        context_score = min(1.0, model.context_window / 128000)

        # Provider quality tiers (estimated)
        provider_scores = {
            "anthropic": 0.95,
            "openai": 0.90,
            "gemini": 0.85,
            "azure": 0.90,
            "openrouter": 0.80,
            "ollama": 0.70,
            "lmstudio": 0.70,
            "copilot": 0.85,
        }
        provider_score = provider_scores.get(model.provider.lower(), 0.5)

        return (context_score + provider_score) / 2

    def _score_speed(self, model: ModelConfig) -> float:
        """Score model speed."""
        # Check historical performance
        perf = self._model_performance.get(model.name, {})
        if "avg_latency_ms" in perf:
            # Lower latency = higher score
            return max(0.0, 1.0 - (perf["avg_latency_ms"] / 10000))

        # Default: local models are faster
        if model.provider.lower() in ("ollama", "lmstudio"):
            return 0.8
        return 0.5

    def _score_cost(self, model: ModelConfig) -> float:
        """Score model cost (lower = higher score)."""
        # Free/local models get highest score
        if model.cost_per_1k_input == 0:
            return 1.0

        # Scale inversely with cost
        max_cost = 0.06  # $0.06/1k is expensive
        return max(0.0, 1.0 - (model.cost_per_1k_input / max_cost))

    def _score_capability(self, model: ModelConfig, task_type: TaskType) -> float:
        """Score model capability match for task."""
        score = 0.5  # Base score

        # Bonus for relevant capabilities
        if task_type == TaskType.CODING:
            if model.supports_tools:
                score += 0.3
            if model.context_window >= 32000:
                score += 0.2
        elif task_type == TaskType.ANALYSIS:
            if model.context_window >= 64000:
                score += 0.4
        elif task_type == TaskType.REVIEW:
            if model.supports_tools:
                score += 0.2

        return min(1.0, score)

    def record_performance(
        self, model: str, latency_ms: float, tokens_per_second: float
    ) -> None:
        """Record model performance for future selection."""
        if model not in self._model_performance:
            self._model_performance[model] = {}

        perf = self._model_performance[model]

        # Running average
        if "avg_latency_ms" in perf:
            perf["avg_latency_ms"] = (perf["avg_latency_ms"] + latency_ms) / 2
        else:
            perf["avg_latency_ms"] = latency_ms

        if "avg_tokens_per_second" in perf:
            perf["avg_tokens_per_second"] = (
                perf["avg_tokens_per_second"] + tokens_per_second
            ) / 2
        else:
            perf["avg_tokens_per_second"] = tokens_per_second
