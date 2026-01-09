import { ProjectAPI, createProjectAPI } from './project-api';
import { TerminalAPI, createTerminalAPI } from './terminal-api';
import { TaskAPI, createTaskAPI } from './task-api';
import { SettingsAPI, createSettingsAPI } from './settings-api';
import { FileAPI, createFileAPI } from './file-api';
import { AgentAPI, createAgentAPI } from './agent-api';
import { IdeationAPI, createIdeationAPI } from './modules/ideation-api';
import { InsightsAPI, createInsightsAPI } from './modules/insights-api';
import { AppUpdateAPI, createAppUpdateAPI } from './app-update-api';
import { GitHubAPI, createGitHubAPI } from './modules/github-api';
import { GitLabAPI, createGitLabAPI } from './modules/gitlab-api';
import { DebugAPI, createDebugAPI } from './modules/debug-api';
import { ClaudeCodeAPI, createClaudeCodeAPI } from './modules/claude-code-api';
import { McpAPI, createMcpAPI } from './modules/mcp-api';
import { ProfileAPI, createProfileAPI } from './profile-api';
import { MemoryAPI, createMemoryAPI } from './memory-api';
import type { Agent, AgentPoolStatus } from '../../main/ipc/agent-ipc';
import type { Episode, MemorySearchOptions, MemorySearchResult, MemoryInsight, MemoryStats } from './memory-api';

// Namespaced Agents API for window.apex.agents
interface AgentsNamespacedAPI {
  list: () => Promise<Agent[]>;
  getPoolStatus: () => Promise<AgentPoolStatus | null>;
  start: (input: { name: string; type: string; config?: Record<string, unknown> }) => Promise<Agent>;
  stop: (id: string) => Promise<void>;
  pause: (id: string) => Promise<void>;
  resume: (id: string) => Promise<void>;
  onStarted: (callback: (agent: Agent) => void) => () => void;
  onStopped: (callback: (agentId: string) => void) => () => void;
  onStatusChanged: (callback: (data: { agentId: string; status: string }) => void) => () => void;
  onPoolUpdated: (callback: (status: AgentPoolStatus) => void) => () => void;
}

// Namespaced Tasks API for window.apex.tasks
interface TasksNamespacedAPI {
  list: (projectId?: string) => Promise<unknown[]>;
  create: (data: { title: string; description: string; projectId?: string }) => Promise<unknown>;
  update: (id: string, updates: Record<string, unknown>) => Promise<unknown>;
  delete: (id: string) => Promise<void>;
  onCreated: (callback: (task: unknown) => void) => () => void;
  onUpdated: (callback: (task: unknown) => void) => () => void;
  onDeleted: (callback: (taskId: string) => void) => () => void;
}

// Namespaced Settings API for window.apex.settings
interface SettingsNamespacedAPI {
  getAll: () => Promise<Record<string, unknown>>;
  update: (updates: Record<string, unknown>) => Promise<void>;
  reset: () => Promise<void>;
  onChange: (callback: (settings: Record<string, unknown>) => void) => () => void;
}

// Events API for window.apex.events
interface EventsAPI {
  on: (event: string, callback: (...args: unknown[]) => void) => () => void;
  off: (event: string, callback: (...args: unknown[]) => void) => void;
  emit: (event: string, ...args: unknown[]) => void;
}

// Window API for window.apex.window
interface WindowAPI {
  minimize: () => void;
  maximize: () => void;
  close: () => void;
  isMaximized: () => Promise<boolean>;
}

export interface ElectronAPI extends
  ProjectAPI,
  TerminalAPI,
  TaskAPI,
  SettingsAPI,
  FileAPI,
  AgentAPI,
  IdeationAPI,
  InsightsAPI,
  AppUpdateAPI,
  GitLabAPI,
  DebugAPI,
  ClaudeCodeAPI,
  McpAPI,
  ProfileAPI {
  github: GitHubAPI;
  // Namespaced APIs for component compatibility
  agents: AgentsNamespacedAPI;
  memory: MemoryAPI;
  tasks: TasksNamespacedAPI;
  settings: SettingsNamespacedAPI;
  events: EventsAPI;
  window: WindowAPI;
  platform: string;
  onTerminalAuthCreated: (callback: (info: unknown) => void) => () => void;
}

// Create stub namespaced APIs
const createAgentsNamespacedAPI = (): AgentsNamespacedAPI => ({
  list: async () => [],
  getPoolStatus: async () => null,
  start: async () => ({ id: '', name: '', type: 'coder', status: 'idle', config: {}, tasksCompleted: 0, tokensUsed: 0, startedAt: new Date().toISOString(), lastActivityAt: new Date().toISOString() } as Agent),
  stop: async () => {},
  pause: async () => {},
  resume: async () => {},
  onStarted: () => () => {},
  onStopped: () => () => {},
  onStatusChanged: () => () => {},
  onPoolUpdated: () => () => {},
});

const createTasksNamespacedAPI = (): TasksNamespacedAPI => ({
  list: async () => [],
  create: async () => ({}),
  update: async () => ({}),
  delete: async () => {},
  onCreated: () => () => {},
  onUpdated: () => () => {},
  onDeleted: () => () => {},
});

const createSettingsNamespacedAPI = (): SettingsNamespacedAPI => ({
  getAll: async () => ({}),
  update: async () => {},
  reset: async () => {},
  onChange: () => () => {},
});

const createEventsAPI = (): EventsAPI => ({
  on: () => () => {},
  off: () => {},
  emit: () => {},
});

const createWindowAPI = (): WindowAPI => ({
  minimize: () => {},
  maximize: () => {},
  close: () => {},
  isMaximized: async () => false,
});

export const createElectronAPI = (): ElectronAPI => ({
  ...createProjectAPI(),
  ...createTerminalAPI(),
  ...createTaskAPI(),
  ...createSettingsAPI(),
  ...createFileAPI(),
  ...createAgentAPI(),
  ...createIdeationAPI(),
  ...createInsightsAPI(),
  ...createAppUpdateAPI(),
  ...createGitLabAPI(),
  ...createDebugAPI(),
  ...createClaudeCodeAPI(),
  ...createMcpAPI(),
  ...createProfileAPI(),
  github: createGitHubAPI(),
  // Namespaced APIs
  agents: createAgentsNamespacedAPI(),
  memory: createMemoryAPI(),
  tasks: createTasksNamespacedAPI(),
  settings: createSettingsNamespacedAPI(),
  events: createEventsAPI(),
  window: createWindowAPI(),
  platform: process.platform,
  onTerminalAuthCreated: () => () => {},
});

// Export individual API creators for potential use in tests or specialized contexts
export {
  createProjectAPI,
  createTerminalAPI,
  createTaskAPI,
  createSettingsAPI,
  createFileAPI,
  createAgentAPI,
  createIdeationAPI,
  createInsightsAPI,
  createAppUpdateAPI,
  createProfileAPI,
  createGitHubAPI,
  createGitLabAPI,
  createDebugAPI,
  createClaudeCodeAPI,
  createMcpAPI,
  createMemoryAPI
};

export type {
  ProjectAPI,
  TerminalAPI,
  TaskAPI,
  SettingsAPI,
  FileAPI,
  AgentAPI,
  IdeationAPI,
  InsightsAPI,
  AppUpdateAPI,
  ProfileAPI,
  GitHubAPI,
  GitLabAPI,
  DebugAPI,
  ClaudeCodeAPI,
  McpAPI,
  MemoryAPI,
  AgentsNamespacedAPI,
  TasksNamespacedAPI,
  SettingsNamespacedAPI,
  EventsAPI,
  WindowAPI
};
