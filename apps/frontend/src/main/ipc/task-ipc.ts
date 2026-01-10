/**
 * APEX Development Platform - Task IPC Handlers
 * Phase 4: UI, Integrations & Analytics
 *
 * Handles task-related IPC communication between renderer and main process.
 */

import { IpcMain } from 'electron';
import { IPCChannels } from './index';
import { createIPCSuccess, createIPCError, IPCResponse } from './ipc-handler';
import { BackendService } from '../services/backend-service';

/** Task priority levels */
export type TaskPriority = 'critical' | 'high' | 'medium' | 'low';

/** Task status */
export type TaskStatus = 'pending' | 'queued' | 'running' | 'in-progress' | 'completed' | 'failed' | 'cancelled';

/** Task definition */
export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
  agentType?: string;
  agentId?: string;
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
  result?: unknown;
  error?: string;
  metadata?: Record<string, unknown>;
}

/** Create task params */
export interface CreateTaskParams {
  title: string;
  description?: string;
  priority?: TaskPriority;
  agentType?: string;
  metadata?: Record<string, unknown>;
}

/** Update task params */
export interface UpdateTaskParams {
  id: string;
  title?: string;
  description?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  metadata?: Record<string, unknown>;
}

/** Task list filter */
export interface TaskListParams {
  status?: TaskStatus | TaskStatus[];
  priority?: TaskPriority | TaskPriority[];
  agentType?: string;
  limit?: number;
  offset?: number;
  sortBy?: 'createdAt' | 'updatedAt' | 'priority';
  sortOrder?: 'asc' | 'desc';
}

/** Task search params */
export interface TaskSearchParams {
  query: string;
  status?: TaskStatus[];
  limit?: number;
}

/**
 * Register task IPC handlers
 */
export function registerTaskIPCHandlers(ipcMain: IpcMain): void {
  const backend = BackendService.getInstance();

  // Create task
  ipcMain.handle(
    IPCChannels.TASK_CREATE,
    async (_, params: CreateTaskParams): Promise<IPCResponse<Task>> => {
      try {
        const task = await backend.request<Task>('task.create', params);
        return createIPCSuccess(task);
      } catch (error) {
        return createIPCError('TASK_CREATE_FAILED', (error as Error).message);
      }
    }
  );

  // Update task
  ipcMain.handle(
    IPCChannels.TASK_UPDATE,
    async (_, params: UpdateTaskParams): Promise<IPCResponse<Task>> => {
      try {
        const task = await backend.request<Task>('task.update', params);
        return createIPCSuccess(task);
      } catch (error) {
        return createIPCError('TASK_UPDATE_FAILED', (error as Error).message);
      }
    }
  );

  // Delete task
  ipcMain.handle(
    IPCChannels.TASK_DELETE,
    async (_, id: string): Promise<IPCResponse<boolean>> => {
      try {
        await backend.request('task.delete', { id });
        return createIPCSuccess(true);
      } catch (error) {
        return createIPCError('TASK_DELETE_FAILED', (error as Error).message);
      }
    }
  );

  // List tasks
  ipcMain.handle(
    IPCChannels.TASK_LIST,
    async (_, params: TaskListParams = {}): Promise<IPCResponse<Task[]>> => {
      try {
        const tasks = await backend.request<Task[]>('task.list', params);
        return createIPCSuccess(tasks);
      } catch (error) {
        return createIPCError('TASK_LIST_FAILED', (error as Error).message);
      }
    }
  );

  // Get single task
  ipcMain.handle(
    IPCChannels.TASK_GET,
    async (_, id: string): Promise<IPCResponse<Task>> => {
      try {
        const task = await backend.request<Task>('task.get', { id });
        return createIPCSuccess(task);
      } catch (error) {
        return createIPCError('TASK_GET_FAILED', (error as Error).message);
      }
    }
  );

  // Search tasks
  ipcMain.handle(
    IPCChannels.TASK_SEARCH,
    async (_, params: TaskSearchParams): Promise<IPCResponse<Task[]>> => {
      try {
        const tasks = await backend.request<Task[]>('task.search', params);
        return createIPCSuccess(tasks);
      } catch (error) {
        return createIPCError('TASK_SEARCH_FAILED', (error as Error).message);
      }
    }
  );

  console.log('[IPC] Task handlers registered');
}
