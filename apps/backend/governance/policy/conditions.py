"""
Condition Evaluators - Phase 9 Implementation.

Condition evaluation for policy rules with provider awareness.

World-Class Standards:
- Type-safe evaluation
- Provider-specific conditions
- Extensible condition types
"""

import logging
import re
from collections.abc import Callable
from datetime import datetime, time
from typing import Any

from ..models import SUPPORTED_PROVIDERS, RuleOperator

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """
    Evaluates conditions against context data.

    Supports various comparison operators and
    provider-specific condition checks.
    """

    def __init__(self) -> None:
        self._custom_evaluators: dict[str, Callable] = {}

    def evaluate(
        self, field: str, operator: RuleOperator, expected: Any, context: dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition.

        Args:
            field: Field path in context (dot notation)
            operator: Comparison operator
            expected: Expected value
            context: Request context

        Returns:
            True if condition matches
        """
        actual = self._get_field_value(context, field)
        return self._compare(actual, operator, expected)

    def evaluate_provider_condition(
        self, provider: str, condition: str, context: dict[str, Any]
    ) -> bool:
        """
        Evaluate a provider-specific condition.

        Args:
            provider: One of 8 LLM providers
            condition: Condition identifier
            context: Request context

        Returns:
            True if condition passes
        """
        if provider not in SUPPORTED_PROVIDERS:
            logger.warning(f"Unknown provider: {provider}")
            return False

        # Check if we have a custom evaluator
        evaluator_key = f"{provider}:{condition}"
        if evaluator_key in self._custom_evaluators:
            return self._custom_evaluators[evaluator_key](context)

        # Default provider-specific checks
        if condition == "is_enabled":
            return context.get("enabled_providers", {}).get(provider, True)
        elif condition == "is_local":
            return provider in ("ollama", "lmstudio")
        elif condition == "is_paid":
            return provider in ("openrouter", "gemini", "openai", "anthropic", "azure")
        elif condition == "requires_auth":
            return provider not in ("ollama", "lmstudio")
        else:
            logger.debug(f"Unknown condition: {condition}")
            return True

    def _get_field_value(self, context: dict[str, Any], field: str) -> Any:
        """Get value from context using dot notation."""
        if not field:
            return None

        keys = field.split(".")
        value = context

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                idx = int(key)
                value = value[idx] if idx < len(value) else None
            else:
                return None

            if value is None:
                return None

        return value

    def _compare(self, actual: Any, operator: RuleOperator, expected: Any) -> bool:
        """Compare actual value against expected using operator."""
        try:
            if operator == RuleOperator.EQ:
                return actual == expected
            elif operator == RuleOperator.NE:
                return actual != expected
            elif operator == RuleOperator.GT:
                return actual is not None and actual > expected
            elif operator == RuleOperator.GE:
                return actual is not None and actual >= expected
            elif operator == RuleOperator.LT:
                return actual is not None and actual < expected
            elif operator == RuleOperator.LE:
                return actual is not None and actual <= expected
            elif operator == RuleOperator.IN:
                return actual in (expected or [])
            elif operator == RuleOperator.NOT_IN:
                return actual not in (expected or [])
            elif operator == RuleOperator.CONTAINS:
                return expected in str(actual) if actual else False
            elif operator == RuleOperator.STARTS_WITH:
                return str(actual).startswith(str(expected)) if actual else False
            elif operator == RuleOperator.ENDS_WITH:
                return str(actual).endswith(str(expected)) if actual else False
            elif operator == RuleOperator.MATCHES:
                return bool(re.match(str(expected), str(actual))) if actual else False
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except (TypeError, ValueError) as e:
            logger.debug(f"Comparison error: {e}")
            return False

    def register_evaluator(
        self, key: str, evaluator: Callable[[dict[str, Any]], bool]
    ) -> None:
        """Register a custom condition evaluator."""
        self._custom_evaluators[key] = evaluator
        logger.debug(f"Registered custom evaluator: {key}")

    def unregister_evaluator(self, key: str) -> bool:
        """Unregister a custom evaluator."""
        if key in self._custom_evaluators:
            del self._custom_evaluators[key]
            return True
        return False


class TimeCondition:
    """
    Time-based condition evaluation.

    Checks if current time falls within allowed windows.
    """

    @staticmethod
    def is_business_hours(
        context: dict[str, Any],
        start_hour: int = 9,
        end_hour: int = 17,
        timezone: str = "UTC",
    ) -> bool:
        """Check if current time is within business hours."""
        now = datetime.now()
        return start_hour <= now.hour < end_hour

    @staticmethod
    def is_weekend(context: dict[str, Any]) -> bool:
        """Check if today is a weekend."""
        now = datetime.now()
        return now.weekday() >= 5  # Saturday=5, Sunday=6

    @staticmethod
    def is_within_window(
        context: dict[str, Any], start_time: time, end_time: time
    ) -> bool:
        """Check if current time is within a time window."""
        now = datetime.now().time()
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:
            # Window crosses midnight
            return now >= start_time or now <= end_time


class ThresholdCondition:
    """
    Threshold-based condition evaluation.

    Checks if values exceed or fall below thresholds.
    """

    @staticmethod
    def exceeds_threshold(
        context: dict[str, Any], field: str, threshold: float
    ) -> bool:
        """Check if field value exceeds threshold."""
        value = context.get(field, 0)
        try:
            return float(value) > threshold
        except (TypeError, ValueError):
            return False

    @staticmethod
    def below_threshold(context: dict[str, Any], field: str, threshold: float) -> bool:
        """Check if field value is below threshold."""
        value = context.get(field, 0)
        try:
            return float(value) < threshold
        except (TypeError, ValueError):
            return False

    @staticmethod
    def within_range(
        context: dict[str, Any], field: str, min_value: float, max_value: float
    ) -> bool:
        """Check if field value is within range."""
        value = context.get(field, 0)
        try:
            v = float(value)
            return min_value <= v <= max_value
        except (TypeError, ValueError):
            return False
