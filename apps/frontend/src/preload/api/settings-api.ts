/**
 * APEX Development Platform - Settings API (Preload)
 * Phase 4: UI, Integrations & Analytics
 *
 * Application settings API exposed to renderer.
 */

import { ipcRenderer } from 'electron';

/** LLM Provider type */
export type LLMProvider =
  | 'copilot'
  | 'openrouter'
  | 'ollama'
  | 'lmstudio'
  | 'gemini'
  | 'openai'
  | 'anthropic'
  | 'azure';

/** LLM configuration */
export interface LLMConfig {
  provider: LLMProvider;
  apiKey?: string;
  baseUrl?: string;
  model: string;
  temperature?: number;
  maxTokens?: number;
  timeout?: number;
}

/** Integration settings */
export interface IntegrationSettings {
  github?: {
    enabled: boolean;
    token?: string;
    organization?: string;
  };
  gitlab?: {
    enabled: boolean;
    token?: string;
    baseUrl?: string;
  };
  linear?: {
    enabled: boolean;
    apiKey?: string;
    teamId?: string;
  };
  slack?: {
    enabled: boolean;
    webhookUrl?: string;
  };
  jira?: {
    enabled: boolean;
    baseUrl?: string;
    email?: string;
    apiToken?: string;
  };
}

/** UI settings */
export interface UISettings {
  theme: 'light' | 'dark' | 'system';
  fontSize: number;
  fontFamily: string;
  sidebarWidth: number;
  terminalHeight: number;
  showLineNumbers: boolean;
  wordWrap: boolean;
}

/** Agent settings */
export interface AgentSettings {
  maxConcurrentAgents: number;
  defaultAgentType: string;
  autoRetryFailed: boolean;
  retryAttempts: number;
  taskTimeout: number;
}

/** Analytics settings */
export interface AnalyticsSettings {
  enabled: boolean;
  trackUsage: boolean;
  trackCosts: boolean;
  retentionDays: number;
}

/** All settings */
export interface AppSettings {
  llm: LLMConfig;
  integrations: IntegrationSettings;
  ui: UISettings;
  agents: AgentSettings;
  analytics: AnalyticsSettings;
}

/**
 * Settings API
 */
export const settingsAPI = {
  /**
   * Get all settings
   */
  getAll: (): Promise<AppSettings> =>
    ipcRenderer.invoke('settings:getAll'),

  /**
   * Get specific setting section
   */
  get: <K extends keyof AppSettings>(key: K): Promise<AppSettings[K]> =>
    ipcRenderer.invoke('settings:get', key),

  /**
   * Set setting section
   */
  set: <K extends keyof AppSettings>(key: K, value: AppSettings[K]): Promise<void> =>
    ipcRenderer.invoke('settings:set', key, value),

  /**
   * Update partial settings
   */
  update: (settings: Partial<AppSettings>): Promise<void> =>
    ipcRenderer.invoke('settings:update', settings),

  /**
   * Reset to defaults
   */
  reset: (key?: keyof AppSettings): Promise<void> =>
    ipcRenderer.invoke('settings:reset', key),

  /**
   * Export settings to file
   */
  export: (path: string): Promise<boolean> =>
    ipcRenderer.invoke('settings:export', path),

  /**
   * Import settings from file
   */
  import: (path: string): Promise<boolean> =>
    ipcRenderer.invoke('settings:import', path),

  // LLM Provider specific
  /**
   * Get LLM config for provider
   */
  getLLMConfig: (provider: LLMProvider): Promise<LLMConfig | null> =>
    ipcRenderer.invoke('settings:getLLMConfig', provider),

  /**
   * Set LLM config for provider
   */
  setLLMConfig: (provider: LLMProvider, config: Partial<LLMConfig>): Promise<void> =>
    ipcRenderer.invoke('settings:setLLMConfig', provider, config),

  /**
   * Test LLM connection
   */
  testLLMConnection: (provider: LLMProvider): Promise<{ success: boolean; error?: string }> =>
    ipcRenderer.invoke('settings:testLLMConnection', provider),

  /**
   * Get available models for provider
   */
  getAvailableModels: (provider: LLMProvider): Promise<string[]> =>
    ipcRenderer.invoke('settings:getAvailableModels', provider),

  // Integration specific
  /**
   * Test integration connection
   */
  testIntegration: (
    type: keyof IntegrationSettings
  ): Promise<{ success: boolean; error?: string }> =>
    ipcRenderer.invoke('settings:testIntegration', type),

  /**
   * Subscribe to settings changes
   */
  onSettingsChange: (callback: (settings: AppSettings) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, settings: AppSettings) =>
      callback(settings);
    ipcRenderer.on('settings:changed', listener);
    return () => ipcRenderer.removeListener('settings:changed', listener);
  },

  /**
   * Subscribe to specific setting changes
   */
  onSettingChange: <K extends keyof AppSettings>(
    key: K,
    callback: (value: AppSettings[K]) => void
  ) => {
    const listener = (_event: Electron.IpcRendererEvent, k: K, value: AppSettings[K]) => {
      if (k === key) callback(value);
    };
    ipcRenderer.on('settings:settingChanged', listener);
    return () => ipcRenderer.removeListener('settings:settingChanged', listener);
  },
};
