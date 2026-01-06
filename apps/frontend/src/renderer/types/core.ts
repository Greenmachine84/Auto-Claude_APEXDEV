/**
 * APEX Development Platform - Core Types
 * Phase 4: UI, Integrations & Analytics
 */

/** Task status */
export type TaskStatus = 'pending' | 'in-progress' | 'completed' | 'failed' | 'cancelled';

/** Task priority */
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

/** Task interface */
export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignedAgentId?: string;
  parentTaskId?: string;
  subtaskIds: string[];
  labels: string[];
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

/** Agent type */
export type AgentType = 'coder' | 'reviewer' | 'fixer' | 'planner' | 'analyst';

/** Agent status */
export type AgentStatus = 'idle' | 'running' | 'paused' | 'stopped' | 'error';

/** Agent interface */
export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  currentTaskId?: string;
  config: Record<string, unknown>;
  metrics: {
    tasksCompleted: number;
    tokensUsed: number;
    averageDuration: number;
    successRate: number;
  };
  startedAt: string;
  lastActiveAt: string;
}

/** Episode type */
export type EpisodeType = 'task' | 'conversation' | 'code' | 'decision' | 'insight';

/** Episode interface */
export interface Episode {
  id: string;
  content: string;
  metadata: {
    type: EpisodeType;
    source?: string;
    taskId?: string;
    agentId?: string;
    importance?: number;
    tags?: string[];
  };
  embedding?: number[];
  createdAt: string;
  updatedAt: string;
}

/** LLM Provider ID */
export type LLMProviderId =
  | 'copilot'
  | 'openrouter'
  | 'ollama'
  | 'lmstudio'
  | 'gemini'
  | 'openai'
  | 'anthropic'
  | 'azure';

/** LLM Provider config */
export interface LLMProviderConfig {
  enabled: boolean;
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  deploymentName?: string;
}

/** Integration ID */
export type IntegrationId = 'github' | 'gitlab' | 'linear' | 'slack' | 'jira';

/** Integration config */
export interface IntegrationConfig {
  enabled: boolean;
  [key: string]: unknown;
}

/** Settings interface */
export interface Settings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  fontSize: number;
  autoSave: boolean;
  wordWrap: boolean;
  tabSize: number;
  notifications: boolean;
  sounds: boolean;
  defaultProjectPath?: string;
  openLastProject?: boolean;
  defaultLLMProvider: LLMProviderId;
  llmProviders: Partial<Record<LLMProviderId, LLMProviderConfig>>;
  modelPreference: string;
  maxTokens: number;
  temperature: number;
  agentConfig: Record<string, unknown>;
  integrations: Partial<Record<IntegrationId, IntegrationConfig>>;
  keybinds: Record<string, string>;
}

/** IPC Response wrapper */
export interface IPCResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

/** Pagination params */
export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

/** Paginated response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}
