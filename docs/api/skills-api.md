# Skills API Reference

Complete API documentation for the Auto-Claude skills system.

## Overview

The Skills API provides interfaces for defining, composing, and executing
reusable agent capabilities that encapsulate complex behaviors.

## Core Concepts

### Skill Definition

Skills are self-contained units of agent behavior.

```python
from apps.backend.skills import Skill, SkillContext

class CodeReviewSkill(Skill):
    """Skill for reviewing code changes."""

    name = "code_review"
    description = "Review code for issues and improvements"
    version = "1.0.0"

    async def execute(
        self,
        context: SkillContext,
        code: str,
        language: str
    ) -> ReviewResult:
        # Implementation
        pass
```

## Skill Registry

### Registering Skills

```python
from apps.backend.skills import SkillRegistry

registry = SkillRegistry()

# Register by class
registry.register(CodeReviewSkill)

# Register with metadata
registry.register(
    CodeReviewSkill,
    tags=["review", "quality"],
    priority=SkillPriority.HIGH
)

# Register from module
registry.register_module(code_skills)
```

### Retrieving Skills

```python
# Get by name
skill = registry.get("code_review")

# Get by tag
review_skills = registry.get_by_tag("review")

# List all
all_skills = registry.list_all()
```

## Skill Execution

### SkillExecutor

Executes skills with context management.

```python
from apps.backend.skills import SkillExecutor

executor = SkillExecutor(registry=registry)

result = await executor.execute(
    skill_name="code_review",
    params={"code": source_code, "language": "python"},
    context=SkillContext(
        agent_id="agent-123",
        session_id="session-456",
        memory=memory_store
    )
)
```

### Execution Context

```python
@dataclass
class SkillContext:
    agent_id: str
    session_id: str
    memory: Optional[MemoryStore] = None
    tools: Optional[ToolRegistry] = None
    llm: Optional[LLMProvider] = None
    metadata: dict = field(default_factory=dict)
```

## Built-in Skills

### Code Analysis Skills

| Skill | Description | Input | Output |
|-------|-------------|-------|--------|
| `analyze_code` | Static code analysis | `code`, `language` | `AnalysisResult` |
| `detect_patterns` | Pattern detection | `code`, `patterns` | `PatternMatches` |
| `extract_structure` | Extract code structure | `code` | `CodeStructure` |

### Code Generation Skills

| Skill | Description | Input | Output |
|-------|-------------|-------|--------|
| `generate_code` | Generate code from spec | `spec`, `language` | `GeneratedCode` |
| `refactor_code` | Refactor existing code | `code`, `changes` | `RefactoredCode` |
| `generate_tests` | Generate test cases | `code`, `framework` | `TestSuite` |

### Documentation Skills

| Skill | Description | Input | Output |
|-------|-------------|-------|--------|
| `generate_docs` | Generate documentation | `code` | `Documentation` |
| `explain_code` | Explain code logic | `code` | `Explanation` |
| `generate_readme` | Create README | `project` | `ReadmeContent` |

### Review Skills

| Skill | Description | Input | Output |
|-------|-------------|-------|--------|
| `code_review` | Review code changes | `code`, `language` | `ReviewResult` |
| `security_review` | Security analysis | `code` | `SecurityReport` |
| `performance_review` | Performance analysis | `code` | `PerformanceReport` |

## Custom Skill Development

### Basic Skill

```python
from apps.backend.skills import Skill, SkillContext

class SummarizeSkill(Skill):
    name = "summarize"
    description = "Summarize text content"

    async def execute(
        self,
        context: SkillContext,
        text: str,
        max_length: int = 200
    ) -> str:
        response = await context.llm.complete([
            {"role": "user", "content": f"Summarize in {max_length} chars:\n{text}"}
        ])
        return response.content
```

### Skill with Dependencies

```python
class AnalyzeAndReviewSkill(Skill):
    name = "analyze_and_review"
    dependencies = ["analyze_code", "code_review"]

    async def execute(
        self,
        context: SkillContext,
        code: str
    ) -> CombinedResult:
        # Use dependent skills
        analysis = await self.call_skill("analyze_code", code=code)
        review = await self.call_skill("code_review", code=code)

        return CombinedResult(analysis=analysis, review=review)
```

### Skill with State

```python
class IncrementalAnalysisSkill(Skill):
    name = "incremental_analysis"

    async def execute(
        self,
        context: SkillContext,
        code: str
    ) -> AnalysisResult:
        # Retrieve previous analysis from memory
        previous = await context.memory.retrieve(
            f"analysis:{context.session_id}"
        )

        # Perform incremental analysis
        result = await self._analyze(code, previous)

        # Store for next invocation
        await context.memory.store(
            MemoryEntry(
                id=f"analysis:{context.session_id}",
                content=json.dumps(result.to_dict()),
                category=MemoryCategory.WORKING
            )
        )

        return result
```

## Skill Composition

### Sequential Composition

```python
from apps.backend.skills import SkillPipeline

pipeline = SkillPipeline([
    ("analyze", "analyze_code", {}),
    ("review", "code_review", {"include_analysis": True}),
    ("summarize", "summarize_review", {})
])

result = await executor.execute_pipeline(pipeline, code=source_code)
```

### Parallel Composition

```python
from apps.backend.skills import ParallelSkills

parallel = ParallelSkills([
    ("security", "security_review"),
    ("performance", "performance_review"),
    ("style", "style_review")
])

results = await executor.execute_parallel(parallel, code=source_code)
```

### Conditional Composition

```python
from apps.backend.skills import ConditionalSkill

conditional = ConditionalSkill(
    condition=lambda ctx, r: r.has_security_issues,
    if_true="detailed_security_review",
    if_false="generate_approval"
)

result = await executor.execute_conditional(
    conditional,
    previous_result=review_result
)
```

## Skill Parameters

### Parameter Validation

```python
from apps.backend.skills import Skill, param

class ValidatedSkill(Skill):
    name = "validated_skill"

    @param("code", type=str, required=True)
    @param("language", type=str, choices=["python", "typescript", "rust"])
    @param("depth", type=int, min=1, max=10, default=3)
    async def execute(
        self,
        context: SkillContext,
        code: str,
        language: str,
        depth: int = 3
    ) -> Result:
        pass
```

### Parameter Types

| Type | Description | Validation |
|------|-------------|------------|
| `str` | String value | `min_length`, `max_length`, `pattern` |
| `int` | Integer value | `min`, `max` |
| `float` | Float value | `min`, `max` |
| `bool` | Boolean value | - |
| `list` | List of items | `item_type`, `min_items`, `max_items` |
| `dict` | Dictionary | `schema` |

## Error Handling

### Skill Exceptions

| Exception | Description |
|-----------|-------------|
| `SkillError` | Base skill exception |
| `SkillNotFoundError` | Skill not in registry |
| `ValidationError` | Invalid parameters |
| `DependencyError` | Missing dependency |
| `ExecutionError` | Runtime failure |

### Error Handling Example

```python
class RobustSkill(Skill):
    name = "robust_skill"

    async def execute(self, context: SkillContext, **params) -> Result:
        try:
            return await self._do_work(params)
        except LLMError as e:
            # Retry with fallback
            return await self._fallback(params)
        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            # Log and wrap unknown errors
            logger.error(f"Skill failed: {e}")
            raise SkillError(f"Execution failed: {e}") from e
```

## Monitoring

### Skill Metrics

```python
metrics = executor.get_metrics("code_review")
print(f"Executions: {metrics.total_executions}")
print(f"Success rate: {metrics.success_rate:.1%}")
print(f"Avg duration: {metrics.avg_duration_ms}ms")
```

### Tracing

```python
# Enable skill tracing
executor = SkillExecutor(
    registry=registry,
    tracer=OpenTelemetryTracer()
)

# Traces include skill name, parameters, duration, result
```

## Best Practices

1. **Keep skills focused** - Single responsibility
2. **Validate inputs** - Use parameter decorators
3. **Handle errors gracefully** - Provide fallbacks
4. **Use composition** - Build complex from simple
5. **Document thoroughly** - Include examples
6. **Test extensively** - Unit and integration tests

## See Also

- [Agent API](agent-api.md)
- [Tool API](tool-api.md)
- [Skill Development Guide](../guides/skill-development.md)
