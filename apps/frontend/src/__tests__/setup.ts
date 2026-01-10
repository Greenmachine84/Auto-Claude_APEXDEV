import '@testing-library/jest-dom';
/**
 * Test setup file for Vitest
 */
import { vi, beforeEach, afterEach } from 'vitest';
import { mkdirSync, rmSync, existsSync } from 'fs';
import path from 'path';
import os from 'os';

// Mock electron module globally for all tests
vi.mock('electron', async () => {
  const { EventEmitter } = await vi.importActual<typeof import('events')>('events');
  
  const app = {
    getName: vi.fn(() => 'APEXDEV'),
    getPath: vi.fn((name: string) => {
      const paths: Record<string, string> = {
        userData: path.join(os.tmpdir(), 'test-app-data'),
        home: os.homedir(),
        temp: os.tmpdir()
      };
      return paths[name] || os.tmpdir();
    }),
    getAppPath: vi.fn(() => path.join(os.tmpdir(), 'test-app')),
    getVersion: vi.fn(() => '0.1.0'),
    isPackaged: false,
    on: vi.fn(),
    quit: vi.fn()
  };

  class MockIpcMain extends EventEmitter {
    private handlers: Map<string, Function> = new Map();
    handle(channel: string, handler: Function): void { this.handlers.set(channel, handler); }
    handleOnce(channel: string, handler: Function): void { this.handlers.set(channel, handler); }
    removeHandler(channel: string): void { this.handlers.delete(channel); }
  }

  const ipcMain = new MockIpcMain();
  const ipcRenderer = {
    invoke: vi.fn(),
    send: vi.fn(),
    on: vi.fn(),
    once: vi.fn(),
    removeListener: vi.fn(),
    removeAllListeners: vi.fn(),
    setMaxListeners: vi.fn()
  };

  class BrowserWindow extends EventEmitter {
    webContents = { send: vi.fn(), on: vi.fn(), once: vi.fn() };
    id = 1;
    constructor(_options?: unknown) { super(); }
    loadURL = vi.fn();
    loadFile = vi.fn();
    show = vi.fn();
    hide = vi.fn();
    close = vi.fn();
    destroy = vi.fn();
    isDestroyed = vi.fn(() => false);
    isFocused = vi.fn(() => true);
    focus = vi.fn();
    blur = vi.fn();
    minimize = vi.fn();
    maximize = vi.fn();
    restore = vi.fn();
    isMinimized = vi.fn(() => false);
    isMaximized = vi.fn(() => false);
    setFullScreen = vi.fn();
    isFullScreen = vi.fn(() => false);
    getBounds = vi.fn(() => ({ x: 0, y: 0, width: 1200, height: 800 }));
    setBounds = vi.fn();
    getContentBounds = vi.fn(() => ({ x: 0, y: 0, width: 1200, height: 800 }));
    setContentBounds = vi.fn();
  }

  const dialog = {
    showOpenDialog: vi.fn(() => Promise.resolve({ canceled: false, filePaths: ['/test/path'] })),
    showSaveDialog: vi.fn(() => Promise.resolve({ canceled: false, filePath: '/test/save/path' })),
    showMessageBox: vi.fn(() => Promise.resolve({ response: 0 })),
    showErrorBox: vi.fn()
  };

  return {
    app,
    ipcMain,
    ipcRenderer,
    BrowserWindow,
    dialog,
    contextBridge: { exposeInMainWorld: vi.fn() },
    shell: { openExternal: vi.fn(), openPath: vi.fn(), showItemInFolder: vi.fn() },
    nativeTheme: { themeSource: 'system', shouldUseDarkColors: false, on: vi.fn() },
    screen: { getPrimaryDisplay: vi.fn(() => ({ workAreaSize: { width: 1920, height: 1080 } })) },
    default: { app, ipcMain, ipcRenderer, BrowserWindow, dialog }
  };
});

// Mock localStorage for tests that need it
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; })
  };
})();

Object.defineProperty(global, 'localStorage', { value: localStorageMock });

if (typeof HTMLElement !== 'undefined' && !HTMLElement.prototype.scrollIntoView) {
  Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', { value: vi.fn(), writable: true });
}

export const TEST_DATA_DIR = path.join(os.tmpdir(), 'APEXDEV-ui-tests');

beforeEach(() => {
  localStorageMock.clear();
  try {
    if (existsSync(TEST_DATA_DIR)) { rmSync(TEST_DATA_DIR, { recursive: true, force: true }); }
  } catch {}
  try {
    mkdirSync(TEST_DATA_DIR, { recursive: true });
    mkdirSync(path.join(TEST_DATA_DIR, 'store'), { recursive: true });
  } catch {}
});

afterEach(() => {
  vi.clearAllMocks();
  vi.resetModules();
});

if (typeof window !== 'undefined') {
  (window as unknown as { electronAPI: unknown }).electronAPI = {
    addProject: vi.fn(),
    removeProject: vi.fn(),
    getProjects: vi.fn(),
    updateProjectSettings: vi.fn(),
    getTasks: vi.fn(),
    createTask: vi.fn(),
    startTask: vi.fn(),
    stopTask: vi.fn(),
    submitReview: vi.fn(),
    onTaskProgress: vi.fn(() => vi.fn()),
    onTaskError: vi.fn(() => vi.fn()),
    onTaskLog: vi.fn(() => vi.fn()),
    onTaskStatusChange: vi.fn(() => vi.fn()),
    getSettings: vi.fn(),
    saveSettings: vi.fn(),
    selectDirectory: vi.fn(),
    getAppVersion: vi.fn(),
    getTabState: vi.fn().mockResolvedValue({ success: true, data: { openProjectIds: [], activeProjectId: null, tabOrder: [] } }),
    saveTabState: vi.fn().mockResolvedValue({ success: true }),
    getAPIProfiles: vi.fn(),
    saveAPIProfile: vi.fn(),
    updateAPIProfile: vi.fn(),
    deleteAPIProfile: vi.fn(),
    setActiveAPIProfile: vi.fn(),
    testConnection: vi.fn()
  };
}

const originalConsoleError = console.error;
console.error = (...args: unknown[]) => {
  const message = args[0]?.toString() || '';
  if (message.includes('[TEST]')) { originalConsoleError(...args); }
};