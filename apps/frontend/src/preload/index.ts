/**
 * APEX Development Platform - Preload Script
 * Phase 4: UI, Integrations & Analytics
 *
 * Exposes secure APIs to the renderer process via contextBridge.
 */

import { contextBridge, ipcRenderer } from 'electron';
import { taskAPI } from './api/task-api';
import { agentAPI } from './api/agent-api';
import { memoryAPI } from './api/memory-api';
import { settingsAPI } from './api/settings-api';

/**
 * Platform utilities
 */
const platformAPI = {
  platform: process.platform,
  isMac: process.platform === 'darwin',
  isWindows: process.platform === 'win32',
  isLinux: process.platform === 'linux',
  versions: {
    electron: process.versions.electron,
    chrome: process.versions.chrome,
    node: process.versions.node,
  },
};

/**
 * Window controls
 */
const windowAPI = {
  minimize: () => ipcRenderer.invoke('window:minimize'),
  maximize: () => ipcRenderer.invoke('window:maximize'),
  close: () => ipcRenderer.invoke('window:close'),
  isMaximized: () => ipcRenderer.invoke('window:isMaximized'),
  setTitle: (title: string) => ipcRenderer.invoke('window:setTitle', title),
};

/**
 * Event subscriptions
 */
const eventsAPI = {
  on: (channel: string, callback: (...args: unknown[]) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, ...args: unknown[]) => callback(...args);
    ipcRenderer.on(channel, listener);
    return () => ipcRenderer.removeListener(channel, listener);
  },
  once: (channel: string, callback: (...args: unknown[]) => void) => {
    ipcRenderer.once(channel, (_event, ...args) => callback(...args));
  },
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  },
};

/**
 * Dialog utilities
 */
const dialogAPI = {
  openFile: (options?: Electron.OpenDialogOptions) =>
    ipcRenderer.invoke('dialog:openFile', options),
  openDirectory: (options?: Electron.OpenDialogOptions) =>
    ipcRenderer.invoke('dialog:openDirectory', options),
  saveFile: (options?: Electron.SaveDialogOptions) =>
    ipcRenderer.invoke('dialog:saveFile', options),
  showMessage: (options: Electron.MessageBoxOptions) =>
    ipcRenderer.invoke('dialog:showMessage', options),
  showError: (title: string, content: string) =>
    ipcRenderer.invoke('dialog:showError', title, content),
};

/**
 * Shell utilities
 */
const shellAPI = {
  openExternal: (url: string) => ipcRenderer.invoke('shell:openExternal', url),
  openPath: (path: string) => ipcRenderer.invoke('shell:openPath', path),
  showItemInFolder: (path: string) => ipcRenderer.invoke('shell:showItemInFolder', path),
};

/**
 * Clipboard utilities
 */
const clipboardAPI = {
  writeText: (text: string) => ipcRenderer.invoke('clipboard:writeText', text),
  readText: () => ipcRenderer.invoke('clipboard:readText'),
  writeHTML: (html: string) => ipcRenderer.invoke('clipboard:writeHTML', html),
  readHTML: () => ipcRenderer.invoke('clipboard:readHTML'),
};

/**
 * Expose APIs to renderer
 */
contextBridge.exposeInMainWorld('apex', {
  platform: platformAPI,
  window: windowAPI,
  events: eventsAPI,
  dialog: dialogAPI,
  shell: shellAPI,
  clipboard: clipboardAPI,
  tasks: taskAPI,
  agents: agentAPI,
  memory: memoryAPI,
  settings: settingsAPI,
});

/**
 * Type declarations for window.apex
 */
declare global {
  interface Window {
    apex: {
      platform: typeof platformAPI;
      window: typeof windowAPI;
      events: typeof eventsAPI;
      dialog: typeof dialogAPI;
      shell: typeof shellAPI;
      clipboard: typeof clipboardAPI;
      tasks: typeof taskAPI;
      agents: typeof agentAPI;
      memory: typeof memoryAPI;
      settings: typeof settingsAPI;
    };
  }
}
