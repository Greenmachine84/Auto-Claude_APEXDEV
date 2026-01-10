/**
 * APEX Development Platform - useSettings Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useState, useEffect, useCallback } from 'react';
import type { Settings } from '../../preload/api/settings-api';

/** Settings hook return type */
export interface UseSettingsReturn {
  settings: Settings;
  loading: boolean;
  error: Error | null;
  // Operations
  updateSettings: (updates: Partial<Settings>) => Promise<void>;
  resetSettings: () => Promise<void>;
  // Specific getters
  getSetting: <K extends keyof Settings>(key: K) => Settings[K];
}

/** Default settings */
const defaultSettings: Settings = { theme: 'system', defaultModel: 'claude-3-opus', agentFramework: 'apex', autoUpdateAutoBuild: true, autoNameTerminals: true,
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
 * Settings Hook - Manage application settings
 */
export function useSettings(): UseSettingsReturn {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Load settings
  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const loaded = await window.apex.settings.getAll();
      setSettings({ ...defaultSettings, ...loaded });
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load settings'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  // Subscribe to settings changes
  useEffect(() => {
    const unsubscribe = window.apex.settings.onChange((newSettings) => {
      setSettings((prev) => ({ ...prev, ...newSettings }));
    });
    return unsubscribe;
  }, []);

  // Update settings
  const updateSettings = useCallback(async (updates: Partial<Settings>): Promise<void> => {
    try {
      await window.apex.settings.update(updates);
      setSettings((prev) => ({ ...prev, ...updates }));
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to update settings'));
      throw err;
    }
  }, []);

  // Reset settings
  const resetSettings = useCallback(async (): Promise<void> => {
    try {
      await window.apex.settings.reset();
      setSettings(defaultSettings);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to reset settings'));
      throw err;
    }
  }, []);

  // Get specific setting
  const getSetting = useCallback(
    <K extends keyof Settings>(key: K): Settings[K] => {
      return settings[key];
    },
    [settings]
  );

  return {
    settings,
    loading,
    error,
    updateSettings,
    resetSettings,
    getSetting,
  };
}

