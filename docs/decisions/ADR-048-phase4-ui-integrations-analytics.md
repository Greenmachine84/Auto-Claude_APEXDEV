# ADR-048: Phase 4 - UI, Integrations & Analytics Architecture

**Status:** Accepted  
**Date:** 2025-01-28  
**Authors:** APEX Development Team  
**Reviewers:** Architecture Council  

## Context

APEX Development Platform requires a comprehensive UI layer, third-party integrations, and analytics capabilities to provide a complete enterprise development experience. This ADR documents the architectural decisions for Phase 4 implementation.

## Decision

### 1. Frontend Architecture

#### 1.1 Technology Stack
- **Framework:** React 18+ with TypeScript strict mode
- **State Management:** Zustand with devtools and persist middleware
- **Styling:** CSS Variables with theme support (light/dark/system)
- **IPC Communication:** Electron contextBridge with typed channels

#### 1.2 Component Structure
```
renderer/
├── components/
│   ├── common/          # Shared UI components (Button, Input, Modal, etc.)
│   ├── kanban/           # Task kanban board components
│   ├── terminal/         # Terminal emulator components
│   ├── agents/           # Agent management components
│   ├── memory/           # Episodic memory components
│   ├── workflow/         # Visual workflow designer
│   ├── settings/         # Settings panels
│   └── analytics/        # Analytics dashboard
├── hooks/                # React hooks for state and IPC
├── store/                # Zustand stores
├── styles/               # Global styles and themes
├── types/                # TypeScript definitions
└── utils/                # Utility functions
```

#### 1.3 IPC Layer
- Type-safe channel definitions in `preload/channels.ts`
- Request/response pattern with error handling
- Event streaming for real-time updates
- Separate handlers for tasks, agents, memory, and settings

### 2. LLM Provider Support

Phase 4 provides equal support for all 8 LLM providers:

| Provider | ID | Features |
|----------|----|---------|
| GitHub Copilot | `copilot` | Native VS Code integration |
| OpenRouter | `openrouter` | Multi-model routing |
| Ollama | `ollama` | Local model execution |
| LM Studio | `lmstudio` | Local model hosting |
| Google Gemini | `gemini` | Google AI models |
| OpenAI | `openai` | GPT models |
| Anthropic | `anthropic` | Claude models |
| Azure OpenAI | `azure` | Enterprise deployment |

### 3. Agent Types

| Type | Purpose | Capabilities |
|------|---------|-------------|
| Coder | Code generation | Write, refactor, optimize code |
| Reviewer | Code review | Analyze, critique, suggest improvements |
| Fixer | Bug fixing | Identify and resolve issues |
| Planner | Task planning | Break down, prioritize, schedule tasks |
| Analyst | Analysis | Performance, security, quality analysis |

### 4. Integration Architecture

#### 4.1 Common Pattern
All integrations follow a consistent pattern:
- `models.py`: Pydantic models for API entities
- `client.py`: Async HTTP client with pagination
- `service.py`: High-level business logic
- `webhooks.py`: Inbound webhook handling

#### 4.2 Supported Integrations

| Integration | API Type | Features |
|-------------|----------|----------|
| GitHub | REST + GraphQL | Repos, PRs, Issues, Reviews |
| GitLab | REST v4 | Projects, MRs, Issues, Notes |
| Linear | GraphQL | Issues, Projects, Teams, Cycles |
| Slack | Web API | Messaging, Channels, Blocks |
| JIRA | REST v3 | Issues, Projects, Sprints, Transitions |

#### 4.3 Webhook Security
- GitHub: HMAC-SHA256 signature verification
- GitLab: Token header verification
- Linear: HMAC-SHA256 signature verification
- Slack: Timestamp + HMAC-SHA256 verification
- JIRA: HMAC-SHA256 signature verification

### 5. Analytics & Metrics

#### 5.1 Tracked Metrics
- Task completion rates by agent type
- Token usage by provider
- Cost tracking and optimization
- Agent performance comparison
- Response time distributions

#### 5.2 Storage
- Time-series data in SQLite/PostgreSQL
- Aggregation for dashboard queries
- Export support for reporting

### 6. State Management

#### 6.1 Store Architecture

| Store | Responsibility | Persistence |
|-------|---------------|-------------|
| appStore | Global app state, settings | Yes |
| taskStore | Task CRUD, filtering | Session |
| agentStore | Agent lifecycle, pool status | Session |
| memoryStore | Episodic memory, search | Session |
| uiStore | Layout, panels, focus mode | Yes |
| notificationStore | Toast notifications | No |

#### 6.2 IPC Event Flow
```
Main Process → IPC → Preload → Renderer → Store → Components
```

### 7. Security Considerations

- API keys stored in secure settings (never in store state)
- Webhook signatures verified before processing
- CORS and CSP configured for Electron
- IPC channels validated in preload script

## Consequences

### Positive
- Consistent architecture across all integrations
- Type-safe communication between main and renderer
- Flexible theming with CSS variables
- Modular stores with clear separation of concerns
- Production-ready webhook security

### Negative
- Increased complexity in IPC layer
- Multiple stores require coordination
- Integration maintenance across 5 platforms

### Mitigations
- Comprehensive TypeScript types reduce errors
- Centralized error handling in IPC handlers
- Shared patterns reduce integration boilerplate

## Implementation Status

### Completed (Phase 4.1 - 4.22)
- [x] IPC Core (channels, error handling, types)
- [x] IPC Handlers (task, agent, memory, settings)
- [x] Main Process Services (backend, git, terminal, notification)
- [x] Menu System (app menu, context menu)
- [x] Preload Layer (API bridge, event streaming)
- [x] Renderer Entry (App component, routing)
- [x] Common Components (Button, Input, Select, Modal, Card, etc.)
- [x] Kanban Components (Board, Column, Card, TaskCard, etc.)
- [x] Terminal Components (TerminalView, TerminalTabs, XTerm integration)
- [x] Agent Components (AgentView, AgentList, AgentCard, etc.)
- [x] Memory Components (MemoryView, EpisodeList, InsightsList)
- [x] Workflow Components (Canvas, Node, Edge, Toolbar)
- [x] Settings Components (General, LLM, Agent, Integration, Keybind)
- [x] Analytics Components (Dashboard, Charts, Metrics)
- [x] React Hooks (useTasks, useAgents, useMemory, useSettings, etc.)
- [x] Zustand Stores (app, task, agent, memory, ui, notification)
- [x] Styles & Utils (globals.css, theme, formatters, validators)
- [x] GitHub Integration (client, service, webhooks)
- [x] GitLab Integration (client, service, webhooks)
- [x] Linear Integration (client, service, webhooks)
- [x] Slack Integration (client, service, webhooks)
- [x] JIRA Integration (client, service, webhooks)

### Files Committed
- **Phase 4.1-4.22:** 132 files across 22 commits
- **Total Lines:** ~12,000+ lines of TypeScript/Python code

## References

- [PHASE4_UI_INTEGRATIONS_ANALYTICS_ARCHITECTURE.md](../architecture/PHASE4_UI_INTEGRATIONS_ANALYTICS_ARCHITECTURE.md)
- [Electron IPC Documentation](https://www.electronjs.org/docs/latest/api/ipc-main)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitLab API](https://docs.gitlab.com/ee/api/)
- [Linear GraphQL API](https://developers.linear.app/docs/graphql/working-with-the-graphql-api)
- [Slack Web API](https://api.slack.com/web)
- [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
