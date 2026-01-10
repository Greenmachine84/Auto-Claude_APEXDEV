/**
 * APEX Development Platform - App Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { LLMProviderId } from '../../preload/api/settings-api';

/** View types for navigation */
export type ViewType =
  | 'kanban'
  | 'terminal'
  | 'agents'
  | 'memory'
  | 'workflow'
  | 'settings'
  | 'analytics';

/** Theme setting */
export type ThemeSetting = 'light' | 'dark' | 'system';

/** Settings interface matching what the app expects */
export interface Settings {
  theme: ThemeSetting;
  language: string;
  fontSize: number;
  autoSave: boolean;
  wordWrap: boolean;
  tabSize: number;
  notifications: boolean;
  sounds: boolean;
  defaultLLMProvider: LLMProviderId;
  llmProviders: Record<string, unknown>;
  modelPreference: string;
  maxTokens: number;
  temperature: number;
  agentConfig: {
    maxConcurrent: number;
    timeout: number;
    defaultType: string;
    autoRetry: boolean;
    maxRetries: number;
    verbose: boolean;
    useMemory: boolean;
    memoryContextLength: number;
    similarityThreshold: number;
    requireApproval: boolean;
    notifyOnComplete: boolean;
  };
  integrations: Record<string, unknown>;
  keybinds: Record<string, string>;
  // UI settings nested for compatibility
  ui: {
    theme: ThemeSetting;
    terminalHeight: number;
    sidebarWidth: number;
  };
}

/** App state */
export interface AppState {
  // Initialization
  initialized: boolean;
  isInitialized: boolean; // Alias for initialized
  loading: boolean;
  error: Error | null;

  // Settings
  settings: Settings;

  // Navigation
  currentView: ViewType;

  // Active context
  currentProject: string | null;
  currentWorkspace: string | null;
}

/** App actions */
export interface AppActions {
  // Initialization
  initialize: () => Promise<void>;
  setError: (error: Error | null) => void;

  // Settings
  updateSettings: (updates: Partial<Settings>) => Promise<void>;
  resetSettings: () => Promise<void>;

  // Navigation
  setCurrentView: (view: ViewType) => void;

  // Project
  setCurrentProject: (path: string | null) => void;
  setCurrentWorkspace: (path: string | null) => void;

  // LLM
  setDefaultLLMProvider: (provider: LLMProviderId) => void;
}

/** Default settings */
const defaultSettings: Settings = {
  theme: 'dark',
  language: 'en',
  fontSize: 14,
  autoSave: true,
  wordWrap: true,
  tabSize: 2,
  notifications: true,
  sounds: false,
  defaultLLMProvider: 'copilot',
  llmProviders: {},
  modelPreference: 'auto',
  maxTokens: 4096,
  temperature: 0.7,
  agentConfig: {
    maxConcurrent: 3,
    timeout: 300,
    defaultType: 'coder',
    autoRetry: true,
    maxRetries: 3,
    verbose: false,
    useMemory: true,
    memoryContextLength: 10,
    similarityThreshold: 0.7,
    requireApproval: false,
    notifyOnComplete: true,
  },
  integrations: {},
  keybinds: {},
  ui: {
    theme: 'dark',
    terminalHeight: 300,
    sidebarWidth: 280,
  },
};

/**
 * App Store - Global application state
 */
export const useAppStore = create<AppState & AppActions>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        initialized: false,
        isInitialized: false, // Alias
        loading: false,
        error: null,
        settings: defaultSettings,
        currentView: 'kanban',
        currentProject: null,
        currentWorkspace: null,

        // Initialize app
        initialize: async () => {
          if (get().initialized) return;

          set({ loading: true, error: null });
          try {
            // Load settings from backend
            const backendSettings = await window.apex.settings.getAll();
            
            // Merge with defaults, ensuring ui object exists
            const mergedSettings: Settings = {
              ...defaultSettings,
              ...backendSettings,
              ui: {
                ...defaultSettings.ui,
                ...(backendSettings?.ui || {}),
                // Also check for top-level theme
                theme: (backendSettings?.ui as any)?.theme || (backendSettings as any)?.theme || defaultSettings.theme,
              },
            };
            
            set({
              initialized: true,
              isInitialized: true,
              loading: false,
              settings: mergedSettings,
            });
          } catch (error) {
            console.error('[AppStore] Initialization error:', error);
            // Still mark as initialized with defaults so app renders
            set({
              initialized: true,
              isInitialized: true,
              loading: false,
              settings: defaultSettings,
              error: error instanceof Error ? error : new Error('Initialization failed'),
            });
          }
        },

        // Set error
        setError: (error) => set({ error }),

        // Update settings
        updateSettings: async (updates) => {
          const currentSettings = get().settings;
          const newSettings = { ...currentSettings, ...updates };
          set({ settings: newSettings });
          try {
            await window.apex.settings.update(updates);
          } catch (error) {
            console.error('[AppStore] Failed to save settings:', error);
          }
        },

        // Reset settings
        resetSettings: async () => {
          set({ settings: defaultSettings });
          try {
            await window.apex.settings.reset();
          } catch (error) {
            console.error('[AppStore] Failed to reset settings:', error);
          }
        },

        // Set current view
        setCurrentView: (view) => set({ currentView: view }),

        // Set current project
        setCurrentProject: (path) => set({ currentProject: path }),

        // Set current workspace
        setCurrentWorkspace: (path) => set({ currentWorkspace: path }),

        // Set default LLM provider
        setDefaultLLMProvider: (provider) => {
          const settings = get().settings;
          set({
            settings: {
              ...settings,
              defaultLLMProvider: provider,
            },
          });
        },
      }),
      {
        name: 'apex-app-store',
        partialize: (state) => ({
          settings: state.settings,
          currentProject: state.currentProject,
          currentView: state.currentView,
        }),
      }
    ),
    { name: 'AppStore' }
  )
);


