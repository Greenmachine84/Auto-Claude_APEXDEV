/**
 * APEX Development Platform - Agent IPC Handlers
 * Phase 4: UI, Integrations & Analytics
 *
 * Handles agent-related IPC communication between renderer and main process.
 */

import { IpcMain } from 'electron';
import { IPCChannels } from './index';
import { createIPCSuccess, createIPCError, IPCResponse } from './ipc-handler';
import { BackendService } from '../services/backend-service';

/** Agent types */
export type AgentType = 'coder' | 'reviewer' | 'fixer' | 'planner';

/** Agent status */
export type AgentStatus = 'idle' | 'busy' | 'starting' | 'stopping' | 'error';

/** Agent definition */
export interface Agent {
  id: string;
  type: AgentType;
  name: string;
  status: AgentStatus;
  currentTaskId?: string;
  startedAt?: string;
  lastActivityAt?: string;
  tasksCompleted: number;
  tokensUsed: number;
  config: AgentConfig;
}

/** Agent configuration */
export interface AgentConfig {
  model?: string;
  provider?: string;
  maxTokens?: number;
  temperature?: number;
  timeout?: number;
}

/** Agent pool status */
export interface AgentPoolStatus {
  totalAgents: number;
  activeAgents: number;
  idleAgents: number;
  queuedTasks: number;
  utilizationPercent: number;
}

/** Agent log entry */
export interface AgentLog {
  timestamp: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  agentId: string;
  taskId?: string;
  metadata?: Record<string, unknown>;
}

/** Start agent params */
export interface StartAgentParams {
  type: AgentType;
  config?: AgentConfig;
}

/** Agent logs params */
export interface AgentLogsParams {
  agentId: string;
  limit?: number;
  level?: AgentLog['level'];
  since?: string;
}

/**
 * Register agent IPC handlers
 */
export function registerAgentIPCHandlers(ipcMain: IpcMain): void {
  const backend = BackendService.getInstance();

  // Start agent
  ipcMain.handle(
    IPCChannels.AGENT_START,
    async (_, params: StartAgentParams): Promise<IPCResponse<Agent>> => {
      try {
        const agent = await backend.request<Agent>('agent.start', params);
        return createIPCSuccess(agent);
      } catch (error) {
        return createIPCError('AGENT_START_FAILED', (error as Error).message);
      }
    }
  );

  // Stop agent
  ipcMain.handle(
    IPCChannels.AGENT_STOP,
    async (_, agentId: string): Promise<IPCResponse<boolean>> => {
      try {
        await backend.request('agent.stop', { id: agentId });
        return createIPCSuccess(true);
      } catch (error) {
        return createIPCError('AGENT_STOP_FAILED', (error as Error).message);
      }
    }
  );

  // Get agent status
  ipcMain.handle(
    IPCChannels.AGENT_STATUS,
    async (_, agentId: string): Promise<IPCResponse<Agent>> => {
      try {
        const agent = await backend.request<Agent>('agent.status', { id: agentId });
        return createIPCSuccess(agent);
      } catch (error) {
        return createIPCError('AGENT_STATUS_FAILED', (error as Error).message);
      }
    }
  );

  // Get agent logs
  ipcMain.handle(
    IPCChannels.AGENT_LOGS,
    async (_, params: AgentLogsParams): Promise<IPCResponse<AgentLog[]>> => {
      try {
        const logs = await backend.request<AgentLog[]>('agent.logs', params);
        return createIPCSuccess(logs);
      } catch (error) {
        return createIPCError('AGENT_LOGS_FAILED', (error as Error).message);
      }
    }
  );

  // List all agents
  ipcMain.handle(
    IPCChannels.AGENT_LIST,
    async (): Promise<IPCResponse<Agent[]>> => {
      try {
        const agents = await backend.request<Agent[]>('agent.list', {});
        return createIPCSuccess(agents);
      } catch (error) {
        return createIPCError('AGENT_LIST_FAILED', (error as Error).message);
      }
    }
  );

  // Get/update agent config
  ipcMain.handle(
    IPCChannels.AGENT_CONFIG,
    async (_, params: { agentId: string; config?: AgentConfig }): Promise<IPCResponse<AgentConfig>> => {
      try {
        const config = await backend.request<AgentConfig>('agent.config', params);
        return createIPCSuccess(config);
      } catch (error) {
        return createIPCError('AGENT_CONFIG_FAILED', (error as Error).message);
      }
    }
  );

  // Get pool status
  ipcMain.handle(
    IPCChannels.AGENT_POOL_STATUS,
    async (): Promise<IPCResponse<AgentPoolStatus>> => {
      try {
        const status = await backend.request<AgentPoolStatus>('agent.pool_status', {});
        return createIPCSuccess(status);
      } catch (error) {
        return createIPCError('AGENT_POOL_STATUS_FAILED', (error as Error).message);
      }
    }
  );

  console.log('[IPC] Agent handlers registered');
}
