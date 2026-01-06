/**
 * APEX Development Platform - Settings IPC Handlers
 * Phase 4: UI, Integrations & Analytics
 *
 * Handles settings-related IPC communication between renderer and main process.
 */

import { IpcMain, nativeTheme, app } from 'electron';
import * as fs from 'fs/promises';
import * as path from 'path';
import { IPCChannels } from './index';
import { createIPCSuccess, createIPCError, IPCResponse } from './ipc-handler';

/** Theme setting */
export type ThemeSetting = 'light' | 'dark' | 'system';

/** LLM Provider */
export type LLMProvider = 'copilot' | 'openrouter' | 'ollama' | 'lmstudio' | 'gemini' | 'openai' | 'anthropic' | 'azure';

/** Provider configuration */
export interface ProviderConfig {
  enabled: boolean;
  apiKey?: string;
  endpoint?: string;
  defaultModel?: string;
}

/** Application settings */
export interface AppSettings {
  general: {
    theme: ThemeSetting;
    language: string;
    autoUpdate: boolean;
    telemetry: boolean;
  };
  llm: {
    defaultProvider: LLMProvider;
    providers: Record<LLMProvider, ProviderConfig>;
    maxTokens: number;
    temperature: number;
  };
  agents: {
    maxConcurrent: number;
    defaultTimeout: number;
    autoRetry: boolean;
    retryCount: number;
  };
  memory: {
    l1MaxSize: number;
    l2MaxSize: number;
    retentionDays: number;
    autoArchive: boolean;
  };
  integrations: {
    github: { enabled: boolean; token?: string };
    gitlab: { enabled: boolean; token?: string };
    linear: { enabled: boolean; apiKey?: string };
    slack: { enabled: boolean; token?: string };
    jira: { enabled: boolean; baseUrl?: string; token?: string };
  };
  ui: {
    sidebarCollapsed: boolean;
    terminalHeight: number;
    kanbanColumns: string[];
  };
}

/** Default settings */
const DEFAULT_SETTINGS: AppSettings = {
  general: {
    theme: 'system',
    language: 'en',
    autoUpdate: true,
    telemetry: false,
  },
  llm: {
    defaultProvider: 'copilot',
    providers: {
      copilot: { enabled: true },
      openrouter: { enabled: false },
      ollama: { enabled: false, endpoint: 'http://localhost:11434' },
      lmstudio: { enabled: false, endpoint: 'http://localhost:1234' },
      gemini: { enabled: false },
      openai: { enabled: false },
      anthropic: { enabled: false },
      azure: { enabled: false },
    },
    maxTokens: 4096,
    temperature: 0.7,
  },
  agents: {
    maxConcurrent: 4,
    defaultTimeout: 300,
    autoRetry: true,
    retryCount: 3,
  },
  memory: {
    l1MaxSize: 100,
    l2MaxSize: 1000,
    retentionDays: 90,
    autoArchive: true,
  },
  integrations: {
    github: { enabled: false },
    gitlab: { enabled: false },
    linear: { enabled: false },
    slack: { enabled: false },
    jira: { enabled: false },
  },
  ui: {
    sidebarCollapsed: false,
    terminalHeight: 300,
    kanbanColumns: ['pending', 'running', 'completed'],
  },
};

let cachedSettings: AppSettings | null = null;

/**
 * Get settings file path
 */
function getSettingsPath(): string {
  return path.join(app.getPath('userData'), 'settings.json');
}

/**
 * Load settings from disk
 */
async function loadSettings(): Promise<AppSettings> {
  if (cachedSettings) return cachedSettings;

  try {
    const data = await fs.readFile(getSettingsPath(), 'utf-8');
    cachedSettings = { ...DEFAULT_SETTINGS, ...JSON.parse(data) };
  } catch {
    cachedSettings = { ...DEFAULT_SETTINGS };
  }
  return cachedSettings;
}

/**
 * Save settings to disk
 */
async function saveSettings(settings: AppSettings): Promise<void> {
  cachedSettings = settings;
  await fs.writeFile(getSettingsPath(), JSON.stringify(settings, null, 2), 'utf-8');
}

/**
 * Register settings IPC handlers
 */
export function registerSettingsIPCHandlers(ipcMain: IpcMain): void {
  // Get all settings
  ipcMain.handle(
    IPCChannels.SETTINGS_GET,
    async (): Promise<IPCResponse<AppSettings>> => {
      try {
        const settings = await loadSettings();
        return createIPCSuccess(settings);
      } catch (error) {
        return createIPCError('SETTINGS_GET_FAILED', (error as Error).message);
      }
    }
  );

  // Update settings
  ipcMain.handle(
    IPCChannels.SETTINGS_SET,
    async (_, updates: Partial<AppSettings>): Promise<IPCResponse<AppSettings>> => {
      try {
        const current = await loadSettings();
        const updated = deepMerge(current, updates);
        await saveSettings(updated);

        // Apply theme if changed
        if (updates.general?.theme) {
          nativeTheme.themeSource = updates.general.theme;
        }

        return createIPCSuccess(updated);
      } catch (error) {
        return createIPCError('SETTINGS_SET_FAILED', (error as Error).message);
      }
    }
  );

  // Reset settings to defaults
  ipcMain.handle(
    IPCChannels.SETTINGS_RESET,
    async (): Promise<IPCResponse<AppSettings>> => {
      try {
        await saveSettings({ ...DEFAULT_SETTINGS });
        nativeTheme.themeSource = 'system';
        return createIPCSuccess({ ...DEFAULT_SETTINGS });
      } catch (error) {
        return createIPCError('SETTINGS_RESET_FAILED', (error as Error).message);
      }
    }
  );

  // Export settings
  ipcMain.handle(
    IPCChannels.SETTINGS_EXPORT,
    async (): Promise<IPCResponse<string>> => {
      try {
        const settings = await loadSettings();
        // Exclude sensitive data
        const exportable = { ...settings };
        Object.keys(exportable.llm.providers).forEach((key) => {
          const provider = key as LLMProvider;
          if (exportable.llm.providers[provider].apiKey) {
            exportable.llm.providers[provider].apiKey = '***';
          }
        });
        return createIPCSuccess(JSON.stringify(exportable, null, 2));
      } catch (error) {
        return createIPCError('SETTINGS_EXPORT_FAILED', (error as Error).message);
      }
    }
  );

  // Import settings
  ipcMain.handle(
    IPCChannels.SETTINGS_IMPORT,
    async (_, settingsJson: string): Promise<IPCResponse<AppSettings>> => {
      try {
        const imported = JSON.parse(settingsJson) as Partial<AppSettings>;
        const current = await loadSettings();
        const merged = deepMerge(current, imported);
        await saveSettings(merged);
        return createIPCSuccess(merged);
      } catch (error) {
        return createIPCError('SETTINGS_IMPORT_FAILED', (error as Error).message);
      }
    }
  );

  // Theme handlers
  ipcMain.handle(IPCChannels.THEME_GET, async (): Promise<IPCResponse<ThemeSetting>> => {
    const settings = await loadSettings();
    return createIPCSuccess(settings.general.theme);
  });

  ipcMain.handle(
    IPCChannels.THEME_SET,
    async (_, theme: ThemeSetting): Promise<IPCResponse<ThemeSetting>> => {
      nativeTheme.themeSource = theme;
      const settings = await loadSettings();
      settings.general.theme = theme;
      await saveSettings(settings);
      return createIPCSuccess(theme);
    }
  );

  console.log('[IPC] Settings handlers registered');
}

/**
 * Deep merge utility
 */
function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const result = { ...target };
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const sourceValue = source[key];
      const targetValue = result[key];
      if (isObject(targetValue) && isObject(sourceValue)) {
        result[key] = deepMerge(targetValue, sourceValue) as T[typeof key];
      } else if (sourceValue !== undefined) {
        result[key] = sourceValue as T[typeof key];
      }
    }
  }
  return result;
}

function isObject(item: unknown): item is Record<string, unknown> {
  return item !== null && typeof item === 'object' && !Array.isArray(item);
}
