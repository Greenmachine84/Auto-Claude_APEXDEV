# Phase 3: Skills, Tools & Orchestration Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 3 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026

---

## Overview

Phase 3 establishes the skills framework, tools system, and orchestration layer. This includes 10+ skill types, 25+ tools, TaskQueue, AgentPool, and workflow engine from DEVAPEX.

---

## Directory Structure

```
apps/
└── backend/
    ├── skills/
    │   ├── __init__.py                    # Skills framework exports
    │   │
    │   ├── core/
    │   │   ├── __init__.py                # Core skills exports
    │   │   ├── base_skill.py              # Abstract skill base class
    │   │   ├── skill_registry.py          # Skill registration
    │   │   ├── skill_executor.py          # Skill execution engine
    │   │   └── skill_config.py            # Skill configuration
    │   │
    │   ├── coding/
    │   │   ├── __init__.py                # Coding skills exports
    │   │   ├── code_generation.py         # Generate code from specs
    │   │   ├── code_refactoring.py        # Refactor existing code
    │   │   ├── code_explanation.py        # Explain code functionality
    │   │   └── code_translation.py        # Translate between languages
    │   │
    │   ├── testing/
    │   │   ├── __init__.py                # Testing skills exports
    │   │   ├── test_generation.py         # Generate test cases
    │   │   ├── test_execution.py          # Run tests and collect results
    │   │   └── coverage_analysis.py       # Analyze test coverage
    │   │
    │   ├── review/
    │   │   ├── __init__.py                # Review skills exports
    │   │   ├── code_review.py             # Perform code reviews
    │   │   ├── security_review.py         # Security-focused review
    │   │   └── architecture_review.py     # Architecture assessment
    │   │
    │   ├── documentation/
    │   │   ├── __init__.py                # Doc skills exports
    │   │   ├── docstring_generation.py    # Generate docstrings
    │   │   ├── readme_generation.py       # Generate README files
    │   │   └── api_doc_generation.py      # Generate API documentation
    │   │
    │   ├── analysis/
    │   │   ├── __init__.py                # Analysis skills exports
    │   │   ├── dependency_analysis.py     # Analyze dependencies
    │   │   ├── complexity_analysis.py     # Code complexity metrics
    │   │   └── impact_analysis.py         # Change impact assessment
    │   │
    │   └── types/
    │       ├── __init__.py                # Type exports
    │       ├── skill_types.py             # Skill type enums
    │       └── result_types.py            # Skill result types
    │
    ├── tools/
    │   ├── __init__.py                    # Tools system exports
    │   │
    │   ├── core/
    │   │   ├── __init__.py                # Core tools exports
    │   │   ├── base_tool.py               # Abstract tool base class
    │   │   ├── tool_registry.py           # Tool registration
    │   │   ├── tool_executor.py           # Tool execution engine
    │   │   ├── tool_permissions.py        # Permission management
    │   │   └── tool_sandbox.py            # Sandboxed execution
    │   │
    │   ├── filesystem/
    │   │   ├── __init__.py                # FS tools exports
    │   │   ├── file_read.py               # Read file contents
    │   │   ├── file_write.py              # Write/create files
    │   │   ├── file_edit.py               # Edit existing files
    │   │   ├── file_delete.py             # Delete files
    │   │   ├── directory_list.py          # List directory contents
    │   │   ├── directory_create.py        # Create directories
    │   │   └── file_search.py             # Search files by pattern
    │   │
    │   ├── git/
    │   │   ├── __init__.py                # Git tools exports
    │   │   ├── git_status.py              # Get repository status
    │   │   ├── git_diff.py                # Show file differences
    │   │   ├── git_commit.py              # Commit changes
    │   │   ├── git_branch.py              # Branch operations
    │   │   ├── git_log.py                 # View commit history
    │   │   └── git_worktree.py            # Worktree management
    │   │
    │   ├── terminal/
    │   │   ├── __init__.py                # Terminal tools exports
    │   │   ├── command_execute.py         # Execute shell commands
    │   │   ├── process_spawn.py           # Spawn background processes
    │   │   ├── process_kill.py            # Terminate processes
    │   │   └── output_capture.py          # Capture command output
    │   │
    │   ├── web/
    │   │   ├── __init__.py                # Web tools exports
    │   │   ├── http_request.py            # Make HTTP requests
    │   │   ├── web_scrape.py              # Scrape web pages
    │   │   └── api_call.py                # Call external APIs
    │   │
    │   ├── search/
    │   │   ├── __init__.py                # Search tools exports
    │   │   ├── code_search.py             # Search code symbols
    │   │   ├── grep_search.py             # Pattern-based search
    │   │   └── semantic_search_tool.py    # Semantic code search
    │   │
    │   └── types/
    │       ├── __init__.py                # Type exports
    │       ├── tool_types.py              # Tool type enums
    │       ├── permission_types.py        # Permission enums
    │       └── result_types.py            # Tool result types
    │
    └── orchestrator/
        ├── __init__.py                    # Orchestration exports
        │
        ├── core/
        │   ├── __init__.py                # Core orchestration exports
        │   ├── orchestrator.py            # Main orchestrator class
        │   ├── orchestrator_config.py     # Orchestrator configuration
        │   └── execution_context.py       # Task execution context
        │
        ├── queue/
        │   ├── __init__.py                # Queue exports
        │   ├── task_queue.py              # Priority task queue
        │   ├── task_model.py              # Task data model
        │   ├── queue_persistence.py       # Queue state persistence
        │   └── queue_metrics.py           # Queue performance metrics
        │
        ├── pool/
        │   ├── __init__.py                # Pool exports
        │   ├── agent_pool.py              # Agent instance pool
        │   ├── pool_config.py             # Pool configuration
        │   ├── pool_scaler.py             # Dynamic pool scaling
        │   └── agent_selector.py          # Select agent for task
        │
        ├── workflow/
        │   ├── __init__.py                # Workflow exports
        │   ├── workflow_engine.py         # State machine engine
        │   ├── workflow_definition.py     # Workflow DSL
        │   ├── workflow_state.py          # Workflow state tracking
        │   ├── step_executor.py           # Execute workflow steps
        │   └── workflow_templates.py      # Pre-built workflow templates
        │
        ├── dispatch/
        │   ├── __init__.py                # Dispatch exports
        │   ├── task_dispatcher.py         # Dispatch tasks to agents
        │   ├── priority_scheduler.py      # Priority-based scheduling
        │   ├── load_balancer.py           # Balance load across agents
        │   └── retry_handler.py           # Handle failed task retries
        │
        ├── results/
        │   ├── __init__.py                # Results exports
        │   ├── result_collector.py        # Collect agent results
        │   ├── result_aggregator.py       # Aggregate multi-agent results
        │   └── result_validator.py        # Validate result quality
        │
        └── types/
            ├── __init__.py                # Type exports
            ├── task_types.py              # Task type definitions
            ├── workflow_types.py          # Workflow type definitions
            └── dispatch_types.py          # Dispatch-related types
```

---

## File Specifications

### 1. Skills Core Module (`skills/core/`)

#### `base_skill.py`
**Purpose**: Abstract base class for all skills
**Key Components**:
```python
class BaseSkill(ABC):
    name: str
    description: str
    required_tools: List[str]
    
    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult
    
    def validate_input(self, input_data: dict) -> bool
    def get_dependencies(self) -> List[str]
```

#### `skill_registry.py`
**Purpose**: Central registry for skill discovery
**Key Methods**:
```python
class SkillRegistry:
    def register(self, skill: BaseSkill) -> None
    def get(self, name: str) -> BaseSkill
    def list_by_category(self, category: str) -> List[BaseSkill]
    def find_by_capability(self, capability: str) -> List[BaseSkill]
```

#### `skill_executor.py`
**Purpose**: Execute skills with proper context
**Key Methods**:
```python
class SkillExecutor:
    async def execute(self, skill_name: str, context: SkillContext) -> SkillResult
    async def execute_chain(self, skill_names: List[str], context: SkillContext) -> List[SkillResult]
```

---

### 2. Skill Categories

#### Coding Skills (`skills/coding/`)

| File | Skill | Description |
|------|-------|-------------|
| `code_generation.py` | CodeGenerationSkill | Generate code from natural language specs |
| `code_refactoring.py` | CodeRefactoringSkill | Improve existing code structure |
| `code_explanation.py` | CodeExplanationSkill | Explain what code does |
| `code_translation.py` | CodeTranslationSkill | Translate between programming languages |

#### Testing Skills (`skills/testing/`)

| File | Skill | Description |
|------|-------|-------------|
| `test_generation.py` | TestGenerationSkill | Generate unit/integration tests |
| `test_execution.py` | TestExecutionSkill | Run tests and collect results |
| `coverage_analysis.py` | CoverageAnalysisSkill | Analyze code coverage |

#### Review Skills (`skills/review/`)

| File | Skill | Description |
|------|-------|-------------|
| `code_review.py` | CodeReviewSkill | Comprehensive code review |
| `security_review.py` | SecurityReviewSkill | Security-focused analysis |
| `architecture_review.py` | ArchitectureReviewSkill | Architecture assessment |

#### Documentation Skills (`skills/documentation/`)

| File | Skill | Description |
|------|-------|-------------|
| `docstring_generation.py` | DocstringSkill | Generate function/class docstrings |
| `readme_generation.py` | ReadmeSkill | Generate README documentation |
| `api_doc_generation.py` | ApiDocSkill | Generate API documentation |

#### Analysis Skills (`skills/analysis/`)

| File | Skill | Description |
|------|-------|-------------|
| `dependency_analysis.py` | DependencySkill | Analyze project dependencies |
| `complexity_analysis.py` | ComplexitySkill | Calculate complexity metrics |
| `impact_analysis.py` | ImpactSkill | Assess change impact |

---

### 3. Tools Core Module (`tools/core/`)

#### `base_tool.py`
**Purpose**: Abstract base class for all tools
**Key Components**:
```python
class BaseTool(ABC):
    name: str
    description: str
    parameters: JSONSchema
    permissions: List[Permission]
    
    @abstractmethod
    async def execute(self, params: dict) -> ToolResult
    
    def validate_params(self, params: dict) -> ValidationResult
    def get_schema(self) -> dict
```

#### `tool_registry.py`
**Purpose**: Central registry for tool discovery
**Key Methods**:
```python
class ToolRegistry:
    def register(self, tool: BaseTool) -> None
    def get(self, name: str) -> BaseTool
    def get_for_agent(self, agent_type: AgentType) -> List[BaseTool]
    def get_llm_definitions(self) -> List[dict]
```

#### `tool_permissions.py`
**Purpose**: Manage tool access permissions
**Permission Levels**:
```python
class Permission(Enum):
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_COMMANDS = "execute_commands"
    NETWORK_ACCESS = "network_access"
    GIT_OPERATIONS = "git_operations"
    SPAWN_PROCESSES = "spawn_processes"
```

#### `tool_sandbox.py`
**Purpose**: Sandboxed tool execution
**Features**:
- Resource limits (CPU, memory, time)
- Filesystem isolation
- Network restrictions
- Audit logging

---

### 4. Tool Categories

#### Filesystem Tools (`tools/filesystem/`)

| File | Tool | Description |
|------|------|-------------|
| `file_read.py` | FileReadTool | Read file contents |
| `file_write.py` | FileWriteTool | Write/create files |
| `file_edit.py` | FileEditTool | Edit portions of files |
| `file_delete.py` | FileDeleteTool | Delete files safely |
| `directory_list.py` | DirectoryListTool | List directory contents |
| `directory_create.py` | DirectoryCreateTool | Create directories |
| `file_search.py` | FileSearchTool | Search by glob pattern |

#### Git Tools (`tools/git/`)

| File | Tool | Description |
|------|------|-------------|
| `git_status.py` | GitStatusTool | Get repo status |
| `git_diff.py` | GitDiffTool | Show file diffs |
| `git_commit.py` | GitCommitTool | Commit changes |
| `git_branch.py` | GitBranchTool | Branch operations |
| `git_log.py` | GitLogTool | View commit history |
| `git_worktree.py` | GitWorktreeTool | Manage worktrees |

#### Terminal Tools (`tools/terminal/`)

| File | Tool | Description |
|------|------|-------------|
| `command_execute.py` | CommandExecuteTool | Run shell commands |
| `process_spawn.py` | ProcessSpawnTool | Start background processes |
| `process_kill.py` | ProcessKillTool | Terminate processes |
| `output_capture.py` | OutputCaptureTool | Capture command output |

#### Web Tools (`tools/web/`)

| File | Tool | Description |
|------|------|-------------|
| `http_request.py` | HttpRequestTool | Make HTTP requests |
| `web_scrape.py` | WebScrapeTool | Extract web content |
| `api_call.py` | ApiCallTool | Call REST/GraphQL APIs |

#### Search Tools (`tools/search/`)

| File | Tool | Description |
|------|------|-------------|
| `code_search.py` | CodeSearchTool | Find code symbols |
| `grep_search.py` | GrepSearchTool | Pattern search |
| `semantic_search_tool.py` | SemanticSearchTool | Semantic code search |

---

### 5. Orchestrator Core Module (`orchestrator/core/`)

#### `orchestrator.py`
**Purpose**: Main orchestration engine
**Key Methods**:
```python
class Orchestrator:
    def __init__(self, config: OrchestratorConfig)
    
    async def start(self) -> None
    async def stop(self) -> None
    
    async def submit_task(self, task: Task) -> str
    async def get_task_status(self, task_id: str) -> TaskStatus
    async def cancel_task(self, task_id: str) -> bool
    
    async def run_workflow(self, workflow: Workflow) -> WorkflowResult
```

#### `orchestrator_config.py`
**Purpose**: Orchestrator configuration
**Key Settings**:
```python
@dataclass
class OrchestratorConfig:
    max_concurrent_tasks: int = 10
    max_agents: int = 20
    task_timeout_seconds: int = 3600
    retry_max_attempts: int = 3
    queue_persistence_enabled: bool = True
```

---

### 6. Task Queue Module (`orchestrator/queue/`)

#### `task_queue.py`
**Purpose**: Priority-based task queue
**Key Components**:
```python
class TaskQueue:
    async def enqueue(self, task: Task) -> None
    async def dequeue(self) -> Optional[Task]
    async def peek(self) -> Optional[Task]
    
    def get_by_priority(self, priority: Priority) -> List[Task]
    def get_pending_count(self) -> int
    def get_running_count(self) -> int
```

**Priority Order**: CRITICAL(0) > HIGH(1) > MEDIUM(2) > LOW(3)

#### `task_model.py`
**Purpose**: Task data model
```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    agent_type: Optional[AgentType]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[TaskResult]
    metadata: Dict[str, Any]
```

---

### 7. Agent Pool Module (`orchestrator/pool/`)

#### `agent_pool.py`
**Purpose**: Manage pool of agent instances
**Key Methods**:
```python
class AgentPool:
    def __init__(self, config: PoolConfig)
    
    async def acquire(self, agent_type: AgentType) -> BaseAgent
    async def release(self, agent: BaseAgent) -> None
    
    def get_available_count(self, agent_type: AgentType) -> int
    def get_active_agents(self) -> List[BaseAgent]
    
    async def scale_up(self, agent_type: AgentType, count: int) -> None
    async def scale_down(self, agent_type: AgentType, count: int) -> None
```

#### `pool_scaler.py`
**Purpose**: Dynamic pool scaling
**Strategies**:
- Scale based on queue depth
- Scale based on wait time
- Time-of-day scaling
- Manual override

#### `agent_selector.py`
**Purpose**: Select best agent for task
**Selection Criteria**:
- Agent type match
- Agent availability
- Agent performance history
- Cost considerations

---

### 8. Workflow Module (`orchestrator/workflow/`)

#### `workflow_engine.py`
**Purpose**: Execute multi-step workflows
**Key Methods**:
```python
class WorkflowEngine:
    async def execute(self, workflow: Workflow) -> WorkflowResult
    async def pause(self, workflow_id: str) -> None
    async def resume(self, workflow_id: str) -> None
    async def cancel(self, workflow_id: str) -> None
```

#### `workflow_definition.py`
**Purpose**: Define workflows with DSL
```python
class WorkflowBuilder:
    def step(self, name: str, agent_type: AgentType) -> WorkflowBuilder
    def parallel(self, steps: List[Step]) -> WorkflowBuilder
    def conditional(self, condition: Callable, if_true: Step, if_false: Step) -> WorkflowBuilder
    def loop(self, condition: Callable, body: Step) -> WorkflowBuilder
    def build(self) -> Workflow
```

#### `workflow_templates.py`
**Purpose**: Pre-built workflow templates
**Templates**:
- `CodeReviewWorkflow` - Code → Review → Fix → Review
- `FeatureWorkflow` - Spec → Code → Test → Review → Deploy
- `RefactorWorkflow` - Analyze → Plan → Refactor → Test
- `SecurityAuditWorkflow` - Scan → Red Team → Blue Team → Report

---

### 9. Dispatch Module (`orchestrator/dispatch/`)

#### `task_dispatcher.py`
**Purpose**: Dispatch tasks to available agents
**Key Methods**:
```python
class TaskDispatcher:
    async def dispatch(self, task: Task) -> DispatchResult
    async def dispatch_batch(self, tasks: List[Task]) -> List[DispatchResult]
```

#### `priority_scheduler.py`
**Purpose**: Schedule tasks by priority
**Features**:
- Priority queue integration
- Deadline-aware scheduling
- Starvation prevention

#### `retry_handler.py`
**Purpose**: Handle task failures and retries
**Policies**:
- Exponential backoff
- Maximum retry count
- Circuit breaker pattern

---

### 10. Results Module (`orchestrator/results/`)

#### `result_collector.py`
**Purpose**: Collect results from agents
**Key Methods**:
```python
class ResultCollector:
    async def collect(self, task_id: str) -> TaskResult
    async def wait_for_completion(self, task_id: str, timeout: int) -> TaskResult
```

#### `result_aggregator.py`
**Purpose**: Aggregate results from parallel tasks
**Strategies**:
- Merge results
- Majority voting
- Quality-weighted selection

#### `result_validator.py`
**Purpose**: Validate result quality
**Checks**:
- Completeness
- Correctness criteria
- APEX compliance

---

## Integration Points

### With Agent System (Phase 1)
- Skills use agents for execution
- Tools provided to agents via registry
- Orchestrator spawns agents from pool

### With Memory System (Phase 2)
- Skill results stored as episodes
- Workflow history tracked
- Context retrieved for tasks

### With UI (Phase 4)
- Task status updates via events
- Workflow visualization
- Tool permission dialogs

---

## APEX Compliance

### Governance
- Tool permissions validated before execution
- Sandboxed execution for safety
- Audit trails for all operations

### Memory-First
- All task results stored
- Workflow execution logged
- Skill outcomes tracked

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `skills/core/` | 4 | Skill framework core |
| `skills/coding/` | 4 | Coding skills |
| `skills/testing/` | 3 | Testing skills |
| `skills/review/` | 3 | Review skills |
| `skills/documentation/` | 3 | Doc skills |
| `skills/analysis/` | 3 | Analysis skills |
| `skills/types/` | 2 | Skill types |
| `tools/core/` | 5 | Tool framework core |
| `tools/filesystem/` | 7 | FS tools |
| `tools/git/` | 6 | Git tools |
| `tools/terminal/` | 4 | Terminal tools |
| `tools/web/` | 3 | Web tools |
| `tools/search/` | 3 | Search tools |
| `tools/types/` | 3 | Tool types |
| `orchestrator/core/` | 3 | Orchestrator core |
| `orchestrator/queue/` | 4 | Task queue |
| `orchestrator/pool/` | 4 | Agent pool |
| `orchestrator/workflow/` | 5 | Workflow engine |
| `orchestrator/dispatch/` | 4 | Task dispatch |
| `orchestrator/results/` | 3 | Result handling |
| `orchestrator/types/` | 3 | Orchestrator types |
| **Total** | **79** | Phase 3 files |

---

## Next Steps

→ Phase 4: UI, Integrations & Analytics Architecture
