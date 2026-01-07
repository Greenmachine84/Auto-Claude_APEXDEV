/**
 * APEX Development Platform - IPC Exports
 * Phase 4: UI, Integrations & Analytics
 *
 * Centralized IPC handler registration and channel definitions.
 * All IPC communication flows through these typed handlers.
 */

import { IpcMain } from 'electron';
import { registerTaskIPCHandlers } from './task-ipc';
import { registerAgentIPCHandlers } from './agent-ipc';
import { registerMemoryIPCHandlers } from './memory-ipc';
import { registerSettingsIPCHandlers } from './settings-ipc';

/**
 * IPC Channel definitions
 * Centralized channel naming for type safety
 */
export const IPCChannels = {
  // Task channels
  TASK_CREATE: 'task:create',
  TASK_UPDATE: 'task:update',
  TASK_DELETE: 'task:delete',
  TASK_LIST: 'task:list',
  TASK_GET: 'task:get',
  TASK_SEARCH: 'task:search',
  TASK_STATUS_CHANGED: 'task:status-changed',

  // Agent channels
  AGENT_START: 'agent:start',
  AGENT_STOP: 'agent:stop',
  AGENT_STATUS: 'agent:status',
  AGENT_LOGS: 'agent:logs',
  AGENT_LIST: 'agent:list',
  AGENT_CONFIG: 'agent:config',
  AGENT_POOL_STATUS: 'agent:pool-status',
  AGENT_STATUS_CHANGED: 'agent:status-changed',

  // Memory channels
  MEMORY_SEARCH: 'memory:search',
  MEMORY_GET: 'memory:get',
  MEMORY_STORE: 'memory:store',
  MEMORY_DELETE: 'memory:delete',
  MEMORY_EPISODES: 'memory:episodes',
  MEMORY_INSIGHTS: 'memory:insights',

  // Settings channels
  SETTINGS_GET_ALL: 'settings:getAll',
  SETTINGS_GET: 'settings:get',
  SETTINGS_SET: 'settings:set',
  SETTINGS_UPDATE: 'settings:update',
  SETTINGS_RESET: 'settings:reset',
  SETTINGS_EXPORT: 'settings:export',
  SETTINGS_IMPORT: 'settings:import',
  SETTINGS_CHANGED: 'settings:changed',

  // App channels
  APP_VERSION: 'app:version',
  APP_QUIT: 'app:quit',
  APP_RELOAD: 'app:reload',
  APP_OPEN_EXTERNAL: 'app:open-external',
  APP_SHOW_NOTIFICATION: 'app:show-notification',

  // Theme channels
  THEME_GET: 'theme:get',
  THEME_SET: 'theme:set',
  THEME_CHANGED: 'theme:changed',

  // Window channels
  WINDOW_MINIMIZE: 'window:minimize',
  WINDOW_MAXIMIZE: 'window:maximize',
  WINDOW_CLOSE: 'window:close',
  WINDOW_TOGGLE_FULLSCREEN: 'window:toggle-fullscreen',
} as const;

/**
 * IPC Channel type for type safety
 */
export type IPCChannel = (typeof IPCChannels)[keyof typeof IPCChannels];

/**
 * Register all IPC handlers
 */
export function registerAllIPCHandlers(ipcMain: IpcMain): void {
  console.log('[IPC] Registering all IPC handlers...');

  // Register domain-specific handlers
  registerTaskIPCHandlers(ipcMain);
  registerAgentIPCHandlers(ipcMain);
  registerMemoryIPCHandlers(ipcMain);
  registerSettingsIPCHandlers(ipcMain);

  console.log('[IPC] All IPC handlers registered');
}

// Re-export handlers for testing
export { registerTaskIPCHandlers } from './task-ipc';
export { registerAgentIPCHandlers } from './agent-ipc';
export { registerMemoryIPCHandlers } from './memory-ipc';
export { registerSettingsIPCHandlers } from './settings-ipc';
