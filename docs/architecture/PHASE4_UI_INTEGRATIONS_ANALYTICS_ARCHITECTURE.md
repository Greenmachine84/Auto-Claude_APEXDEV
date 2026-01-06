# Phase 4: UI, Integrations & Analytics Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 4 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026

---

## Overview

Phase 4 establishes the desktop UI (React/Electron), external integrations (GitHub, GitLab, Linear), and analytics dashboard. This includes Kanban board, terminal grid, memory viewer, and real-time agent monitoring.

---

## Directory Structure

```
apps/
└── frontend/
    ├── src/
    │   ├── main/                          # Electron main process
    │   │   ├── index.ts                   # Main entry point
    │   │   ├── app.ts                     # App lifecycle
    │   │   ├── window-manager.ts          # Window management
    │   │   │
    │   │   ├── ipc/
    │   │   │   ├── index.ts               # IPC exports
    │   │   │   ├── ipc-handler.ts         # Main IPC handler
    │   │   │   ├── task-ipc.ts            # Task-related IPC
    │   │   │   ├── agent-ipc.ts           # Agent-related IPC
    │   │   │   ├── memory-ipc.ts          # Memory-related IPC
    │   │   │   └── settings-ipc.ts        # Settings IPC
    │   │   │
    │   │   ├── services/
    │   │   │   ├── index.ts               # Service exports
    │   │   │   ├── backend-service.ts     # Backend communication
    │   │   │   ├── git-service.ts         # Git operations
    │   │   │   ├── terminal-service.ts    # Terminal management
    │   │   │   └── notification-service.ts # Native notifications
    │   │   │
    │   │   └── menu/
    │   │       ├── index.ts               # Menu exports
    │   │       ├── app-menu.ts            # Application menu
    │   │       └── context-menu.ts        # Context menus
    │   │
    │   ├── preload/                       # Preload scripts
    │   │   ├── index.ts                   # Preload entry
    │   │   └── api/
    │   │       ├── index.ts               # API exports
    │   │       ├── task-api.ts            # Task API bridge
    │   │       ├── agent-api.ts           # Agent API bridge
    │   │       ├── memory-api.ts          # Memory API bridge
    │   │       └── settings-api.ts        # Settings API bridge
    │   │
    │   └── renderer/                      # React renderer
    │       ├── index.tsx                  # Renderer entry
    │       ├── App.tsx                    # Root component
    │       │
    │       ├── components/
    │       │   ├── common/                # Shared components
    │       │   │   ├── index.ts
    │       │   │   ├── Button.tsx
    │       │   │   ├── Card.tsx
    │       │   │   ├── Modal.tsx
    │       │   │   ├── Dropdown.tsx
    │       │   │   ├── Input.tsx
    │       │   │   ├── Badge.tsx
    │       │   │   ├── Spinner.tsx
    │       │   │   └── Toast.tsx
    │       │   │
    │       │   ├── kanban/                # Kanban board
    │       │   │   ├── index.ts
    │       │   │   ├── KanbanBoard.tsx      # Main board component
    │       │   │   ├── KanbanColumn.tsx     # Column component
    │       │   │   ├── KanbanCard.tsx       # Task card
    │       │   │   ├── TaskDetail.tsx       # Task detail modal
    │       │   │   ├── CreateTask.tsx       # Create task dialog
    │       │   │   └── PriorityBadge.tsx    # Priority indicator
    │       │   │
    │       │   ├── terminal/              # Terminal grid
    │       │   │   ├── index.ts
    │       │   │   ├── TerminalGrid.tsx     # Grid layout
    │       │   │   ├── TerminalPane.tsx     # Single terminal
    │       │   │   ├── TerminalTabs.tsx     # Tab management
    │       │   │   ├── TerminalOutput.tsx   # Output display
    │       │   │   └── TerminalControls.tsx # Terminal controls
    │       │   │
    │       │   ├── agents/                # Agent monitoring
    │       │   │   ├── index.ts
    │       │   │   ├── AgentList.tsx        # List of agents
    │       │   │   ├── AgentCard.tsx        # Agent status card
    │       │   │   ├── AgentDetail.tsx      # Agent detail view
    │       │   │   ├── AgentLogs.tsx        # Agent output logs
    │       │   │   └── AgentPool.tsx        # Pool visualization
    │       │   │
    │       │   ├── memory/                # Memory viewer
    │       │   │   ├── index.ts
    │       │   │   ├── MemoryView.tsx       # Main memory view
    │       │   │   ├── EpisodeList.tsx      # Episode browser
    │       │   │   ├── EpisodeDetail.tsx    # Episode detail
    │       │   │   ├── MemorySearch.tsx     # Search interface
    │       │   │   └── InsightsPanel.tsx    # Learning insights
    │       │   │
    │       │   ├── workflow/              # Workflow visualization
    │       │   │   ├── index.ts
    │       │   │   ├── WorkflowView.tsx     # Workflow display
    │       │   │   ├── WorkflowNode.tsx     # Step node
    │       │   │   ├── WorkflowEdge.tsx     # Connections
    │       │   │   └── WorkflowStatus.tsx   # Progress status
    │       │   │
    │       │   ├── settings/              # Settings pages
    │       │   │   ├── index.ts
    │       │   │   ├── SettingsPage.tsx     # Settings container
    │       │   │   ├── GeneralSettings.tsx  # General config
    │       │   │   ├── LLMSettings.tsx      # LLM provider config
    │       │   │   ├── AgentSettings.tsx    # Agent limits config
    │       │   │   ├── MemorySettings.tsx   # Memory config
    │       │   │   └── IntegrationSettings.tsx # External integrations
    │       │   │
    │       │   └── analytics/             # Analytics dashboard
    │       │       ├── index.ts
    │       │       ├── Dashboard.tsx        # Main dashboard
    │       │       ├── UsageChart.tsx       # Token/cost charts
    │       │       ├── TaskMetrics.tsx      # Task statistics
    │       │       ├── AgentMetrics.tsx     # Agent performance
    │       │       └── CostBreakdown.tsx    # Cost analysis
    │       │
    │       ├── hooks/                     # React hooks
    │       │   ├── index.ts
    │       │   ├── useTasks.ts            # Task management
    │       │   ├── useAgents.ts           # Agent state
    │       │   ├── useMemory.ts           # Memory access
    │       │   ├── useWebSocket.ts        # Real-time updates
    │       │   ├── useSettings.ts         # Settings state
    │       │   └── useAnalytics.ts        # Analytics data
    │       │
    │       ├── store/                     # State management
    │       │   ├── index.ts               # Store exports
    │       │   ├── store.ts               # Zustand store
    │       │   ├── taskSlice.ts           # Task state slice
    │       │   ├── agentSlice.ts          # Agent state slice
    │       │   ├── memorySlice.ts         # Memory state slice
    │       │   ├── uiSlice.ts             # UI state slice
    │       │   └── settingsSlice.ts       # Settings state
    │       │
    │       ├── styles/                    # Styling
    │       │   ├── globals.css            # Global styles
    │       │   ├── theme.ts               # Theme config
    │       │   └── colors.ts              # Color palette
    │       │
    │       ├── utils/                     # Utilities
    │       │   ├── index.ts
    │       │   ├── formatters.ts          # Data formatters
    │       │   ├── validators.ts          # Form validators
    │       │   └── api-client.ts          # API utilities
    │       │
    │       └── types/                     # TypeScript types
    │           ├── index.ts
    │           ├── task.types.ts          # Task types
    │           ├── agent.types.ts         # Agent types
    │           ├── memory.types.ts        # Memory types
    │           ├── workflow.types.ts      # Workflow types
    │           └── api.types.ts           # API types
    │
    └── integrations/                      # External integrations
        ├── __init__.py
        │
        ├── github/
        │   ├── __init__.py
        │   ├── github_client.py       # GitHub API client
        │   ├── github_auth.py         # OAuth/token auth
        │   ├── pr_manager.py          # Pull request ops
        │   ├── issue_manager.py       # Issue operations
        │   ├── repo_manager.py        # Repository ops
        │   └── webhook_handler.py     # Webhook processing
        │
        ├── gitlab/
        │   ├── __init__.py
        │   ├── gitlab_client.py       # GitLab API client
        │   ├── gitlab_auth.py         # OAuth/token auth
        │   ├── mr_manager.py          # Merge request ops
        │   ├── issue_manager.py       # Issue operations
        │   └── webhook_handler.py     # Webhook processing
        │
        ├── linear/
        │   ├── __init__.py
        │   ├── linear_client.py       # Linear API client
        │   ├── linear_auth.py         # OAuth auth
        │   ├── issue_sync.py          # Issue synchronization
        │   ├── project_sync.py        # Project sync
        │   └── webhook_handler.py     # Webhook processing
        │
        ├── slack/
        │   ├── __init__.py
        │   ├── slack_client.py        # Slack API client
        │   ├── slack_auth.py          # OAuth auth
        │   ├── notification_sender.py # Send notifications
        │   └── command_handler.py     # Slash commands
        │
        └── jira/
            ├── __init__.py
            ├── jira_client.py         # JIRA API client
            ├── jira_auth.py           # Auth handling
            ├── issue_sync.py          # Issue synchronization
            └── webhook_handler.py     # Webhook processing
```

---

## File Specifications

### 1. Electron Main Process (`main/`)

#### `index.ts`
**Purpose**: Application entry point
**Key Components**:
- App initialization
- Window creation
- IPC setup
- Backend process spawn

#### `window-manager.ts`
**Purpose**: Manage application windows
**Key Methods**:
```typescript
class WindowManager {
  createMainWindow(): BrowserWindow
  createSettingsWindow(): BrowserWindow
  showNotification(title: string, body: string): void
  setWindowTitle(title: string): void
}
```

#### IPC Handlers (`main/ipc/`)

| File | Purpose | Events |
|------|---------|--------|
| `task-ipc.ts` | Task operations | `task:create`, `task:update`, `task:delete`, `task:list` |
| `agent-ipc.ts` | Agent control | `agent:start`, `agent:stop`, `agent:status`, `agent:logs` |
| `memory-ipc.ts` | Memory access | `memory:search`, `memory:get`, `memory:store` |
| `settings-ipc.ts` | Settings sync | `settings:get`, `settings:set`, `settings:reset` |

---

### 2. Preload Scripts (`preload/`)

#### API Bridge (`preload/api/`)

| File | Exposed API | Methods |
|------|-------------|--------|
| `task-api.ts` | `window.taskApi` | `createTask()`, `updateTask()`, `getTasks()`, `deleteTask()` |
| `agent-api.ts` | `window.agentApi` | `startAgent()`, `stopAgent()`, `getAgentStatus()`, `getLogs()` |
| `memory-api.ts` | `window.memoryApi` | `searchMemory()`, `getEpisode()`, `storeEpisode()` |
| `settings-api.ts` | `window.settingsApi` | `getSettings()`, `updateSettings()`, `resetSettings()` |

---

### 3. React Components

#### Common Components (`components/common/`)

| Component | Purpose | Props |
|-----------|---------|-------|
| `Button.tsx` | Styled button | `variant`, `size`, `onClick`, `disabled` |
| `Card.tsx` | Content card | `title`, `children`, `actions` |
| `Modal.tsx` | Modal dialog | `isOpen`, `onClose`, `title`, `children` |
| `Dropdown.tsx` | Dropdown menu | `options`, `value`, `onChange` |
| `Input.tsx` | Form input | `type`, `value`, `onChange`, `placeholder` |
| `Badge.tsx` | Status badge | `variant`, `label` |
| `Spinner.tsx` | Loading indicator | `size`, `color` |
| `Toast.tsx` | Notifications | `type`, `message`, `duration` |

#### Kanban Components (`components/kanban/`)

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| `KanbanBoard.tsx` | Main board | Columns, drag-drop, filtering |
| `KanbanColumn.tsx` | Status column | Task list, drop zone, count badge |
| `KanbanCard.tsx` | Task card | Priority, agent, status, actions |
| `TaskDetail.tsx` | Detail modal | Full task info, logs, result |
| `CreateTask.tsx` | Create dialog | Form for new tasks |
| `PriorityBadge.tsx` | Priority display | Color-coded priority |

#### Terminal Components (`components/terminal/`)

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| `TerminalGrid.tsx` | Grid layout | Resizable panes, layout save |
| `TerminalPane.tsx` | Single terminal | xterm.js integration |
| `TerminalTabs.tsx` | Tab bar | Multiple sessions |
| `TerminalOutput.tsx` | Output stream | ANSI color support |
| `TerminalControls.tsx` | Controls | Clear, copy, search |

#### Agent Components (`components/agents/`)

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| `AgentList.tsx` | Agent listing | Filter, sort, status |
| `AgentCard.tsx` | Agent summary | Type, status, task count |
| `AgentDetail.tsx` | Full view | Config, history, metrics |
| `AgentLogs.tsx` | Live logs | Real-time streaming |
| `AgentPool.tsx` | Pool view | Capacity, utilization |

#### Memory Components (`components/memory/`)

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| `MemoryView.tsx` | Main view | Tabs for episodes, search |
| `EpisodeList.tsx` | Episode browser | Pagination, filtering |
| `EpisodeDetail.tsx` | Episode view | Full input/output display |
| `MemorySearch.tsx` | Search UI | Full-text and semantic |
| `InsightsPanel.tsx` | Learning display | Patterns, lessons |

#### Workflow Components (`components/workflow/`)

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| `WorkflowView.tsx` | Workflow graph | Node-edge visualization |
| `WorkflowNode.tsx` | Step node | Status, agent type |
| `WorkflowEdge.tsx` | Connections | Conditional styling |
| `WorkflowStatus.tsx` | Progress bar | Step completion |

#### Settings Components (`components/settings/`)

| Component | Purpose | Key Settings |
|-----------|---------|-------------|
| `SettingsPage.tsx` | Container | Tab navigation |
| `GeneralSettings.tsx` | General config | Theme, language, paths |
| `LLMSettings.tsx` | LLM config | API keys, default models |
| `AgentSettings.tsx` | Agent config | Max agents, timeouts |
| `MemorySettings.tsx` | Memory config | Retention, cache sizes |
| `IntegrationSettings.tsx` | Integrations | GitHub, Linear tokens |

#### Analytics Components (`components/analytics/`)

| Component | Purpose | Key Metrics |
|-----------|---------|-------------|
| `Dashboard.tsx` | Main dashboard | Summary cards |
| `UsageChart.tsx` | Token usage | Charts over time |
| `TaskMetrics.tsx` | Task stats | Completion rate, duration |
| `AgentMetrics.tsx` | Agent stats | Utilization, success rate |
| `CostBreakdown.tsx` | Cost analysis | By provider, by agent |

---

### 4. React Hooks (`hooks/`)

| Hook | Purpose | Returns |
|------|---------|--------|
| `useTasks.ts` | Task CRUD | `{ tasks, createTask, updateTask, deleteTask }` |
| `useAgents.ts` | Agent management | `{ agents, startAgent, stopAgent, getStatus }` |
| `useMemory.ts` | Memory access | `{ episodes, search, getEpisode }` |
| `useWebSocket.ts` | Real-time updates | `{ connected, subscribe, unsubscribe }` |
| `useSettings.ts` | Settings state | `{ settings, updateSetting, resetSettings }` |
| `useAnalytics.ts` | Analytics data | `{ usage, metrics, costs }` |

---

### 5. State Management (`store/`)

#### `store.ts`
**Purpose**: Zustand store configuration
**Key Features**:
- Persist middleware for settings
- Devtools integration
- Subscriptions

#### State Slices

| Slice | State | Actions |
|-------|-------|---------|
| `taskSlice.ts` | Tasks, filters, selected | `addTask`, `updateTask`, `removeTask`, `setFilter` |
| `agentSlice.ts` | Agents, pool status | `setAgents`, `updateAgent`, `setPoolStatus` |
| `memorySlice.ts` | Episodes, search results | `setEpisodes`, `addEpisode`, `setSearchResults` |
| `uiSlice.ts` | Modals, sidebar, theme | `openModal`, `closeModal`, `toggleSidebar` |
| `settingsSlice.ts` | All settings | `setSetting`, `resetSettings`, `loadSettings` |

---

### 6. External Integrations

#### GitHub Integration (`integrations/github/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `github_client.py` | API client | `request()`, `paginate()` |
| `github_auth.py` | Authentication | `oauth_flow()`, `validate_token()` |
| `pr_manager.py` | Pull requests | `create_pr()`, `merge_pr()`, `add_review()` |
| `issue_manager.py` | Issues | `create_issue()`, `update_issue()`, `close_issue()` |
| `repo_manager.py` | Repositories | `clone()`, `get_branches()`, `get_commits()` |
| `webhook_handler.py` | Webhooks | `handle_push()`, `handle_pr()` |

#### GitLab Integration (`integrations/gitlab/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `gitlab_client.py` | API client | GraphQL + REST support |
| `gitlab_auth.py` | Authentication | OAuth, personal tokens |
| `mr_manager.py` | Merge requests | `create_mr()`, `merge()`, `approve()` |
| `issue_manager.py` | Issues | CRUD operations |
| `webhook_handler.py` | Webhooks | Event processing |

#### Linear Integration (`integrations/linear/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `linear_client.py` | GraphQL client | Query, mutation support |
| `linear_auth.py` | OAuth | OAuth 2.0 flow |
| `issue_sync.py` | Issue sync | Bidirectional sync |
| `project_sync.py` | Project sync | Project/cycle mapping |
| `webhook_handler.py` | Webhooks | Event handling |

#### Slack Integration (`integrations/slack/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `slack_client.py` | API client | Web API, Events API |
| `slack_auth.py` | OAuth | Workspace installation |
| `notification_sender.py` | Notifications | `send_task_update()`, `send_error()` |
| `command_handler.py` | Slash commands | `/apex status`, `/apex run` |

#### JIRA Integration (`integrations/jira/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `jira_client.py` | REST client | Issue, project API |
| `jira_auth.py` | Authentication | API token, OAuth |
| `issue_sync.py` | Issue sync | Bidirectional sync |
| `webhook_handler.py` | Webhooks | Issue events |

---

## Integration Points

### With Backend (Phases 1-3)
- IPC bridge communicates with Python backend
- Task/agent state synchronized
- Memory queries executed via IPC

### With Orchestrator (Phase 3)
- Task creation triggers queue enqueue
- Agent status reflects pool state
- Workflow visualization shows live state

---

## APEX Compliance

### UI Governance
- Permission dialogs for dangerous operations
- Audit log visible in UI
- Cost tracking prominent

### Memory-First
- All interactions logged
- Episode viewer for transparency
- Search across all history

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `main/` | 3 | Electron main |
| `main/ipc/` | 5 | IPC handlers |
| `main/services/` | 5 | Main services |
| `main/menu/` | 3 | App menus |
| `preload/` | 1 | Preload entry |
| `preload/api/` | 5 | API bridges |
| `renderer/` | 2 | Renderer entry |
| `components/common/` | 9 | Common UI |
| `components/kanban/` | 7 | Kanban board |
| `components/terminal/` | 6 | Terminal grid |
| `components/agents/` | 6 | Agent UI |
| `components/memory/` | 6 | Memory viewer |
| `components/workflow/` | 5 | Workflow viz |
| `components/settings/` | 7 | Settings pages |
| `components/analytics/` | 6 | Analytics |
| `hooks/` | 7 | React hooks |
| `store/` | 7 | State management |
| `styles/` | 3 | Styling |
| `utils/` | 4 | Utilities |
| `types/` | 6 | TypeScript types |
| `integrations/github/` | 7 | GitHub |
| `integrations/gitlab/` | 6 | GitLab |
| `integrations/linear/` | 6 | Linear |
| `integrations/slack/` | 5 | Slack |
| `integrations/jira/` | 5 | JIRA |
| **Total** | **132** | Phase 4 files |

---

## Next Steps

→ Phase 5: Testing, Security & Documentation Architecture
