/**
 * APEX Development Platform - Agent API (Preload)
 * Phase 4: UI, Integrations & Analytics
 *
 * Agent management API exposed to renderer.
 */

import { ipcRenderer } from 'electron';

/** Agent type */
export type AgentType = 'coder' | 'reviewer' | 'fixer' | 'planner' | 'analyst';

/** Agent status */
export type AgentStatus = 'idle' | 'running' | 'paused' | 'error' | 'stopped';

/** Agent data */
export interface Agent {
  id: string;
  type: AgentType;
  status: AgentStatus;
  taskId?: string;
  startedAt?: string;
  lastActiveAt?: string;
  metrics?: AgentMetrics;
}

/** Agent metrics */
export interface AgentMetrics {
  tasksCompleted: number;
  tasksFailed: number;
  avgTaskDuration: number;
  tokenUsage: number;
  costEstimate: number;
}

/** Agent pool status */
export interface AgentPoolStatus {
  totalAgents: number;
  runningAgents: number;
  idleAgents: number;
  queuedTasks: number;
  agentsByType: Record<AgentType, number>;
}

/** Agent start options */
export interface AgentStartOptions {
  taskId?: string;
  config?: Record<string, unknown>;
  priority?: number;
}

/**
 * Agent API
 */
export const agentAPI = {
  /**
   * Start an agent
   */
  start: (type: AgentType, options?: AgentStartOptions): Promise<Agent> =>
    ipcRenderer.invoke('agent:start', type, options),

  /**
   * Stop an agent
   */
  stop: (id: string): Promise<boolean> =>
    ipcRenderer.invoke('agent:stop', id),

  /**
   * Pause an agent
   */
  pause: (id: string): Promise<boolean> =>
    ipcRenderer.invoke('agent:pause', id),

  /**
   * Resume a paused agent
   */
  resume: (id: string): Promise<boolean> =>
    ipcRenderer.invoke('agent:resume', id),

  /**
   * Get agent status
   */
  status: (id: string): Promise<Agent | null> =>
    ipcRenderer.invoke('agent:status', id),

  /**
   * List all agents
   */
  list: (): Promise<Agent[]> =>
    ipcRenderer.invoke('agent:list'),

  /**
   * Get agent logs
   */
  logs: (id: string, limit?: number): Promise<string[]> =>
    ipcRenderer.invoke('agent:logs', id, limit),

  /**
   * Get agent pool status
   */
  poolStatus: (): Promise<AgentPoolStatus> =>
    ipcRenderer.invoke('agent:poolStatus'),

  /**
   * Get agent metrics
   */
  getMetrics: (id: string): Promise<AgentMetrics | null> =>
    ipcRenderer.invoke('agent:getMetrics', id),

  /**
   * Subscribe to agent status changes
   */
  onAgentUpdate: (callback: (agent: Agent) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, agent: Agent) => callback(agent);
    ipcRenderer.on('agent:updated', listener);
    return () => ipcRenderer.removeListener('agent:updated', listener);
  },

  /**
   * Subscribe to agent logs
   */
  onAgentLog: (callback: (agentId: string, log: string) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, agentId: string, log: string) =>
      callback(agentId, log);
    ipcRenderer.on('agent:log', listener);
    return () => ipcRenderer.removeListener('agent:log', listener);
  },

  /**
   * Subscribe to agent errors
   */
  onAgentError: (callback: (agentId: string, error: string) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, agentId: string, error: string) =>
      callback(agentId, error);
    ipcRenderer.on('agent:error', listener);
    return () => ipcRenderer.removeListener('agent:error', listener);
  },

  /**
   * Subscribe to pool status updates
   */
  onPoolUpdate: (callback: (status: AgentPoolStatus) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, status: AgentPoolStatus) =>
      callback(status);
    ipcRenderer.on('agent:poolUpdated', listener);
    return () => ipcRenderer.removeListener('agent:poolUpdated', listener);
  },
};
