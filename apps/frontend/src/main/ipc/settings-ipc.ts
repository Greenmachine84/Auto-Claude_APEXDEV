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

/** Application settings - indexable for compatibility */
export interface AppSettings {
  [key: string]: unknown;  // Index signature for Record<string, unknown> compatibility
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
    theme: ThemeSetting;
    sidebarCollapsed: boolean;
    terminalHeight: number;
    kanbanColumns: string[];
  };
  // Additional settings that components may expect
  fontSize?: number;
  agentConfig?: Record<string, unknown>;
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
    theme: 'dark',
    sidebarCollapsed: false,
    terminalHeight: 300,
    kanbanColumns: ['pending', 'running', 'completed'],
  },
  fontSize: 14,
  agentConfig: {},
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
  return cachedSettings!;
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
  // Get all settings (used by preload settings.getAll())
  ipcMain.handle(
    IPCChannels.SETTINGS_GET_ALL,
    async (): Promise<AppSettings> => {
      try {
        const settings = await loadSettings();
        return settings;
      } catch (error) {
        console.error('[Settings] Error getting all settings:', error);
        return { ...DEFAULT_SETTINGS };
      }
    }
  );

  // Get specific setting section
  ipcMain.handle(
    IPCChannels.SETTINGS_GET,
    async (_, key?: keyof AppSettings): Promise<IPCResponse<AppSettings | AppSettings[keyof AppSettings]>> => {
      try {
        const settings = await loadSettings();
        if (key) {
          return createIPCSuccess(settings[key]);
        }
        return createIPCSuccess(settings);
      } catch (error) {
        return createIPCError('SETTINGS_GET_FAILED', (error as Error).message);
      }
    }
  );

  // Update settings (partial update)
  ipcMain.handle(
    IPCChannels.SETTINGS_UPDATE,
    async (_, updates: Partial<AppSettings>): Promise<void> => {
      try {
        const current = await loadSettings();
        const updated = deepMergeSettings(current, updates);
        await saveSettings(updated);

        // Apply theme if changed
        if (updates.general?.theme) {
          nativeTheme.themeSource = updates.general.theme;
        }
        if (updates.ui?.theme) {
          nativeTheme.themeSource = updates.ui.theme;
        }
      } catch (error) {
        console.error('[Settings] Error updating settings:', error);
        throw error;
      }
    }
  );

  // Set settings (full replacement)
  ipcMain.handle(
    IPCChannels.SETTINGS_SET,
    async (_, key: keyof AppSettings, value: AppSettings[keyof AppSettings]): Promise<void> => {
      try {
        const current = await loadSettings();
        current[key as string] = value;
        await saveSettings(current);

        // Apply theme if changed
        if (key === 'general' && (value as AppSettings['general'])?.theme) {
          nativeTheme.themeSource = (value as AppSettings['general']).theme;
        }
        if (key === 'ui' && (value as AppSettings['ui'])?.theme) {
          nativeTheme.themeSource = (value as AppSettings['ui']).theme;
        }
      } catch (error) {
        console.error('[Settings] Error setting settings:', error);
        throw error;
      }
    }
  );

  // Reset settings to defaults
  ipcMain.handle(
    IPCChannels.SETTINGS_RESET,
    async (_, key?: keyof AppSettings): Promise<void> => {
      try {
        if (key) {
          const current = await loadSettings();
          current[key as string] = DEFAULT_SETTINGS[key];
          await saveSettings(current);
        } else {
          await saveSettings({ ...DEFAULT_SETTINGS });
          nativeTheme.themeSource = 'system';
        }
      } catch (error) {
        console.error('[Settings] Error resetting settings:', error);
        throw error;
      }
    }
  );

  // Export settings
  ipcMain.handle(
    IPCChannels.SETTINGS_EXPORT,
    async (_, filePath?: string): Promise<IPCResponse<string | boolean>> => {
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

        if (filePath) {
          await fs.writeFile(filePath, JSON.stringify(exportable, null, 2), 'utf-8');
          return createIPCSuccess(true);
        }
        return createIPCSuccess(JSON.stringify(exportable, null, 2));
      } catch (error) {
        return createIPCError('SETTINGS_EXPORT_FAILED', (error as Error).message);
      }
    }
  );

  // Import settings
  ipcMain.handle(
    IPCChannels.SETTINGS_IMPORT,
    async (_, input: string): Promise<IPCResponse<AppSettings | boolean>> => {
      try {
        let imported: Partial<AppSettings>;

        // Check if input is a file path or JSON string
        if (input.startsWith('{')) {
          imported = JSON.parse(input) as Partial<AppSettings>;
        } else {
          const data = await fs.readFile(input, 'utf-8');
          imported = JSON.parse(data) as Partial<AppSettings>;
        }

        const current = await loadSettings();
        const merged = deepMergeSettings(current, imported);
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
    return createIPCSuccess(settings.ui?.theme || settings.general.theme);
  });

  ipcMain.handle(
    IPCChannels.THEME_SET,
    async (_, theme: ThemeSetting): Promise<IPCResponse<ThemeSetting>> => {
      nativeTheme.themeSource = theme;
      const settings = await loadSettings();
      settings.general.theme = theme;
      if (settings.ui) {
        settings.ui.theme = theme;
      }
      await saveSettings(settings);
      return createIPCSuccess(theme);
    }
  );

  console.log('[IPC] Settings handlers registered');
}

/**
 * Deep merge utility for AppSettings
 */
function deepMergeSettings(target: AppSettings, source: Partial<AppSettings>): AppSettings {
  const result = { ...target };
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const sourceValue = source[key];
      const targetValue = result[key];
      if (isObject(targetValue) && isObject(sourceValue)) {
        result[key] = deepMergeSettings(
          targetValue as AppSettings, 
          sourceValue as Partial<AppSettings>
        );
      } else if (sourceValue !== undefined) {
        result[key] = sourceValue;
      }
    }
  }
  return result;
}

function isObject(item: unknown): item is Record<string, unknown> {
  return item !== null && typeof item === 'object' && !Array.isArray(item);
}