import { ipcRenderer } from 'electron';

// ============================================
// Component-compatible types (for UI components)
// ============================================

/** Task status for UI components */
export type TaskStatus = 'pending' | 'running' | 'in-progress' | 'completed' | 'failed' | 'cancelled';

/** Task priority levels */
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

/** Task filter for queries */
export type TaskFilter = { 
  status?: TaskStatus; 
  priority?: TaskPriority; 
  assignee?: string; 
  labels?: string[];
  search?: string;
};

/** Task update payload */
export type TaskUpdate = { 
  title?: string; 
  description?: string; 
  status?: TaskStatus; 
  priority?: TaskPriority;
};

/** Create task input */
export type CreateTaskInput = { 
  title: string; 
  description: string; 
  priority?: TaskPriority; 
  metadata?: TaskMetadata;
};

/** Task interface (component-compatible) */
export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  agentType?: string;
  agentId?: string;
  assignedAgentId?: string;
  parentTaskId?: string;
  subtaskIds?: string[];
  labels?: string[];
  metadata?: Record<string, unknown>;
  createdAt: string | Date;
  updatedAt: string | Date;
  startedAt?: string | Date;
  completedAt?: string | Date;
  error?: string;
  result?: unknown;
}

/** Task metadata */
export interface TaskMetadata {
  [key: string]: unknown;
}

// ============================================
// IPC Types (from shared for internal use)
// ============================================

import { IPC_CHANNELS } from '../../shared/constants';
import type {
  IPCResult,
  TaskStartOptions,
  TaskRecoveryResult,
  ImplementationPlan,
  TaskLogs,
  TaskLogStreamChunk
} from '../../shared/types';

export interface TaskAPI {
  // Task Operations
  getTasks: (projectId: string) => Promise<IPCResult<Task[]>>;
  createTask: (
    projectId: string,
    title: string,
    description: string,
    metadata?: TaskMetadata
  ) => Promise<IPCResult<Task>>;
  deleteTask: (taskId: string) => Promise<IPCResult>;
  updateTask: (
    taskId: string,
    updates: { title?: string; description?: string }
  ) => Promise<IPCResult<Task>>;
  startTask: (taskId: string, options?: TaskStartOptions) => void;
  stopTask: (taskId: string) => void;
  submitReview: (
    taskId: string,
    approved: boolean,
    feedback?: string
  ) => Promise<IPCResult>;
  updateTaskStatus: (
    taskId: string,
    status: TaskStatus
  ) => Promise<IPCResult>;
  recoverStuckTask: (
    taskId: string,
    options?: { forceStatus?: TaskStatus }
  ) => Promise<IPCResult<TaskRecoveryResult>>;
  getImplementationPlan: (taskId: string) => Promise<IPCResult<ImplementationPlan | null>>;
  getTaskLogs: (taskId: string, limit?: number) => Promise<IPCResult<TaskLogs | null>>;
  
  // Event listeners
  onTaskLogStream: (
    callback: (chunk: TaskLogStreamChunk) => void
  ) => () => void;
  onTaskUpdate: (callback: (task: Task) => void) => () => void;
  onCreated: (callback: (task: Task) => void) => () => void;
  onUpdated: (callback: (task: Task) => void) => () => void;
  onDeleted: (callback: (taskId: string) => void) => () => void;
}

function invokeIpc<T>(channel: string, ...args: unknown[]): Promise<IPCResult<T>> {
  return ipcRenderer.invoke(channel, ...args);
}

function createIpcListener<T>(channel: string, callback: (data: T) => void): () => void {
  const handler = (_event: Electron.IpcRendererEvent, data: unknown) => callback(data as T);
  ipcRenderer.on(channel, handler);
  return () => ipcRenderer.removeListener(channel, handler);
}

export const taskAPI: TaskAPI = {
  getTasks: (projectId) =>
    invokeIpc(IPC_CHANNELS.TASK_LIST, projectId),
  createTask: (projectId, title, description, metadata) =>
    invokeIpc(IPC_CHANNELS.TASK_CREATE, projectId, title, description, metadata),
  deleteTask: (taskId) =>
    invokeIpc(IPC_CHANNELS.TASK_DELETE, taskId),
  updateTask: (taskId, updates) =>
    invokeIpc(IPC_CHANNELS.TASK_UPDATE, taskId, updates),
  startTask: (taskId, options) =>
    ipcRenderer.send(IPC_CHANNELS.TASK_START, taskId, options),
  stopTask: (taskId) =>
    ipcRenderer.send(IPC_CHANNELS.TASK_STOP, taskId),
  submitReview: (taskId, approved, feedback) =>
    invokeIpc(IPC_CHANNELS.TASK_REVIEW, taskId, approved, feedback),
  updateTaskStatus: (taskId, status) =>
    invokeIpc(IPC_CHANNELS.TASK_UPDATE_STATUS, taskId, status),
  recoverStuckTask: (taskId, options) =>
    invokeIpc(IPC_CHANNELS.TASK_RECOVER_STUCK, taskId, options),
  getImplementationPlan: (taskId) =>
    invokeIpc(IPC_CHANNELS.TASK_LOGS_GET, taskId),
  getTaskLogs: (taskId, limit) =>
    invokeIpc(IPC_CHANNELS.TASK_LOGS_GET, taskId, limit),
  onTaskLogStream: (callback) =>
    createIpcListener<TaskLogStreamChunk>(IPC_CHANNELS.TASK_LOGS_STREAM, callback),
  onTaskUpdate: (callback) =>
    createIpcListener<Task>(IPC_CHANNELS.TASK_STATUS_CHANGE, callback),
  onCreated: (callback) =>
    createIpcListener<Task>(IPC_CHANNELS.TASK_CREATE, callback),
  onUpdated: (callback) =>
    createIpcListener<Task>(IPC_CHANNELS.TASK_UPDATE, callback),
  onDeleted: (callback) =>
    createIpcListener<string>(IPC_CHANNELS.TASK_DELETE, callback),
};

// Factory function for API creation (for preload index.ts)
export const createTaskAPI = (): TaskAPI => taskAPI;