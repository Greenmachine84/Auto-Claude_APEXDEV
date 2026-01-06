/**
 * APEX Development Platform - App Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Settings, LLMProviderId } from '../../preload/api/settings-api';

/** App state */
export interface AppState {
  // Initialization
  initialized: boolean;
  loading: boolean;
  error: Error | null;

  // Settings
  settings: Settings;

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

  // Project
  setCurrentProject: (path: string | null) => void;
  setCurrentWorkspace: (path: string | null) => void;

  // LLM
  setDefaultLLMProvider: (provider: LLMProviderId) => void;
}

/** Default settings */
const defaultSettings: Settings = {
  theme: 'system',
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
        loading: false,
        error: null,
        settings: defaultSettings,
        currentProject: null,
        currentWorkspace: null,

        // Initialize app
        initialize: async () => {
          if (get().initialized) return;

          set({ loading: true, error: null });
          try {
            // Load settings from backend
            const settings = await window.apex.settings.getAll();
            set({
              initialized: true,
              loading: false,
              settings: { ...defaultSettings, ...settings },
            });
          } catch (error) {
            set({
              loading: false,
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
          await window.apex.settings.update(updates);
        },

        // Reset settings
        resetSettings: async () => {
          set({ settings: defaultSettings });
          await window.apex.settings.reset();
        },

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
        }),
      }
    ),
    { name: 'AppStore' }
  )
);
