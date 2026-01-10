import { ipcRenderer } from 'electron';

import { IPC_CHANNELS } from '../../shared/constants';
import type {
  AppSettings as SharedAppSettings,
  IPCResult,
  SourceEnvConfig,
  SourceEnvCheckResult,
  ToolDetectionResult
} from '../../shared/types';

// Extended Settings type that includes all properties used by UI components
export interface Settings {
  // From shared AppSettings
  theme: 'light' | 'dark' | 'system';
  colorTheme?: string;
  defaultModel: string;
  agentFramework: string;
  pythonPath?: string;
  gitPath?: string;
  githubCLIPath?: string;
  claudePath?: string;
  autoBuildPath?: string;
  autoUpdateAutoBuild: boolean;
  autoNameTerminals: boolean;
  notifications?: NotificationSettings | boolean;
  language?: string;
  sentryEnabled?: boolean;
  uiScale?: number;
  betaUpdates?: boolean;
  preferredIDE?: string;
  preferredTerminal?: string;
  
  // Additional settings for UI components
  fontSize?: number;
  autoSave?: boolean;
  wordWrap?: boolean;
  tabSize?: number;
  defaultProjectPath?: string;
  openLastProject?: boolean;
  sounds?: boolean;
  keybinds?: Record<string, string>;
  agentConfig?: Record<string, unknown>;
  
  // Index signature for flexibility
  [key: string]: unknown;
}

// Notification settings type (compatible with shared/types)
export interface NotificationSettings {
  enabled?: boolean;
  sound?: boolean;
  desktop?: boolean;
  email?: boolean;
  slack?: boolean;
}

// Type for compatibility with shared types
export type AppSettings = SharedAppSettings;

export type LLMProviderId = 'copilot' | 'openrouter' | 'ollama' | 'lmstudio' | 'gemini' | 'openai' | 'anthropic' | 'azure';
export interface LLMProviderConfig { enabled: boolean; apiKey?: string; baseUrl?: string; model?: string; deploymentName?: string; }

export interface SettingsAPI {
  // App Settings
  getSettings: () => Promise<IPCResult<Settings>>;
  saveSettings: (settings: Partial<Settings>) => Promise<IPCResult>;

  // CLI Tools Detection
  getCliToolsInfo: () => Promise<IPCResult<{
    python: ToolDetectionResult;
    git: ToolDetectionResult;
    gh: ToolDetectionResult;
    claude: ToolDetectionResult;
  }>>;

  // App Info
  getAppVersion: () => Promise<string>;

  // Auto-Build Source Environment
  getSourceEnv: () => Promise<IPCResult<SourceEnvConfig>>;
  updateSourceEnv: (config: { claudeOAuthToken?: string }) => Promise<IPCResult>;
  checkSourceToken: () => Promise<IPCResult<SourceEnvCheckResult>>;

  // Sentry error reporting
  notifySentryStateChanged: (enabled: boolean) => void;
  getSentryDsn: () => Promise<string>;
  getSentryConfig: () => Promise<{ dsn: string; tracesSampleRate: number; profilesSampleRate: number }>;
}

export const createSettingsAPI = (): SettingsAPI => ({
  // App Settings
  getSettings: (): Promise<IPCResult<Settings>> =>
    ipcRenderer.invoke(IPC_CHANNELS.SETTINGS_GET),

  saveSettings: (settings: Partial<Settings>): Promise<IPCResult> =>
    ipcRenderer.invoke(IPC_CHANNELS.SETTINGS_SAVE, settings),

  // CLI Tools Detection
  getCliToolsInfo: (): Promise<IPCResult<{
    python: ToolDetectionResult;
    git: ToolDetectionResult;
    gh: ToolDetectionResult;
    claude: ToolDetectionResult;
  }>> =>
    ipcRenderer.invoke(IPC_CHANNELS.SETTINGS_GET_CLI_TOOLS_INFO),

  // App Info
  getAppVersion: (): Promise<string> =>
    ipcRenderer.invoke(IPC_CHANNELS.APP_VERSION),

  // Auto-Build Source Environment
  getSourceEnv: (): Promise<IPCResult<SourceEnvConfig>> =>
    ipcRenderer.invoke(IPC_CHANNELS.AUTOBUILD_SOURCE_ENV_GET),

  updateSourceEnv: (config: { claudeOAuthToken?: string }): Promise<IPCResult> =>
    ipcRenderer.invoke(IPC_CHANNELS.AUTOBUILD_SOURCE_ENV_UPDATE, config),

  checkSourceToken: (): Promise<IPCResult<SourceEnvCheckResult>> =>
    ipcRenderer.invoke(IPC_CHANNELS.AUTOBUILD_SOURCE_ENV_CHECK_TOKEN),

  // Sentry error reporting - notify main process when setting changes
  notifySentryStateChanged: (enabled: boolean): void =>
    ipcRenderer.send(IPC_CHANNELS.SENTRY_STATE_CHANGED, enabled),

  // Get Sentry DSN from main process (loaded from environment variable)
  getSentryDsn: (): Promise<string> =>
    ipcRenderer.invoke(IPC_CHANNELS.GET_SENTRY_DSN),

  // Get full Sentry config from main process (DSN + sample rates)
  getSentryConfig: (): Promise<{ dsn: string; tracesSampleRate: number; profilesSampleRate: number }> =>
    ipcRenderer.invoke(IPC_CHANNELS.GET_SENTRY_CONFIG)
});