/**
 * APEX Development Platform - Task API (Preload)
 * Phase 4: UI, Integrations & Analytics
 *
 * Task management API exposed to renderer.
 */

import { ipcRenderer } from 'electron';

/** Task status */
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

/** Task priority */
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

/** Task data */
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  agentType?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  error?: string;
  metadata?: Record<string, unknown>;
}

/** Create task input */
export interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: TaskPriority;
  agentType?: string;
  metadata?: Record<string, unknown>;
}

/** Update task input */
export interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  metadata?: Record<string, unknown>;
}

/** Task filter */
export interface TaskFilter {
  status?: TaskStatus | TaskStatus[];
  priority?: TaskPriority | TaskPriority[];
  agentType?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

/**
 * Task API
 */
export const taskAPI = {
  /**
   * Create a new task
   */
  create: (input: CreateTaskInput): Promise<Task> =>
    ipcRenderer.invoke('task:create', input),

  /**
   * Get task by ID
   */
  get: (id: string): Promise<Task | null> =>
    ipcRenderer.invoke('task:get', id),

  /**
   * Update task
   */
  update: (id: string, input: UpdateTaskInput): Promise<Task> =>
    ipcRenderer.invoke('task:update', id, input),

  /**
   * Delete task
   */
  delete: (id: string): Promise<boolean> =>
    ipcRenderer.invoke('task:delete', id),

  /**
   * List tasks with filter
   */
  list: (filter?: TaskFilter): Promise<Task[]> =>
    ipcRenderer.invoke('task:list', filter),

  /**
   * Search tasks
   */
  search: (query: string): Promise<Task[]> =>
    ipcRenderer.invoke('task:search', query),

  /**
   * Cancel running task
   */
  cancel: (id: string): Promise<boolean> =>
    ipcRenderer.invoke('task:cancel', id),

  /**
   * Retry failed task
   */
  retry: (id: string): Promise<Task> =>
    ipcRenderer.invoke('task:retry', id),

  /**
   * Get task logs
   */
  getLogs: (id: string): Promise<string[]> =>
    ipcRenderer.invoke('task:getLogs', id),

  /**
   * Subscribe to task events
   */
  onTaskUpdate: (callback: (task: Task) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, task: Task) => callback(task);
    ipcRenderer.on('task:updated', listener);
    return () => ipcRenderer.removeListener('task:updated', listener);
  },

  /**
   * Subscribe to task completion
   */
  onTaskComplete: (callback: (task: Task) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, task: Task) => callback(task);
    ipcRenderer.on('task:completed', listener);
    return () => ipcRenderer.removeListener('task:completed', listener);
  },

  /**
   * Subscribe to task errors
   */
  onTaskError: (callback: (task: Task, error: string) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, task: Task, error: string) =>
      callback(task, error);
    ipcRenderer.on('task:error', listener);
    return () => ipcRenderer.removeListener('task:error', listener);
  },

  /**
   * Subscribe to task creation
   */
  onCreated: (callback: (task: Task) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, task: Task) => callback(task);
    ipcRenderer.on('task:created', listener);
    return () => ipcRenderer.removeListener('task:created', listener);
  },

  /**
   * Subscribe to task updates
   */
  onUpdated: (callback: (task: Task) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, task: Task) => callback(task);
    ipcRenderer.on('task:updated', listener);
    return () => ipcRenderer.removeListener('task:updated', listener);
  },

  /**
   * Subscribe to task deletion
   */
  onDeleted: (callback: (taskId: string) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, taskId: string) => callback(taskId);
    ipcRenderer.on('task:deleted', listener);
    return () => ipcRenderer.removeListener('task:deleted', listener);
  },
};
