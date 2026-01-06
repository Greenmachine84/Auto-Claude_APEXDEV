/**
 * APEX Development Platform - useTheme Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useState, useEffect, useCallback } from 'react';

/** Theme type */
export type Theme = 'light' | 'dark';

/** Theme hook return type */
export interface UseThemeReturn {
  theme: Theme;
  isDark: boolean;
  setTheme: (theme: Theme | 'system') => void;
  toggleTheme: () => void;
}

/**
 * Theme Hook - Manage application theme
 */
export function useTheme(): UseThemeReturn {
  const [theme, setThemeState] = useState<Theme>('dark');
  const [preference, setPreference] = useState<Theme | 'system'>('system');

  // Detect system theme
  const getSystemTheme = useCallback((): Theme => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
    }
    return 'dark';
  }, []);

  // Resolve actual theme from preference
  const resolveTheme = useCallback(
    (pref: Theme | 'system'): Theme => {
      return pref === 'system' ? getSystemTheme() : pref;
    },
    [getSystemTheme]
  );

  // Apply theme to DOM
  const applyTheme = useCallback((t: Theme) => {
    document.documentElement.setAttribute('data-theme', t);
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    document.documentElement.classList.add(`theme-${t}`);
  }, []);

  // Initialize theme
  useEffect(() => {
    // Load saved preference
    const saved = localStorage.getItem('apex-theme-preference') as Theme | 'system' | null;
    if (saved) {
      setPreference(saved);
    }
  }, []);

  // Apply theme when preference changes
  useEffect(() => {
    const resolved = resolveTheme(preference);
    setThemeState(resolved);
    applyTheme(resolved);
  }, [preference, resolveTheme, applyTheme]);

  // Listen for system theme changes
  useEffect(() => {
    if (preference !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      const newTheme = e.matches ? 'dark' : 'light';
      setThemeState(newTheme);
      applyTheme(newTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [preference, applyTheme]);

  // Set theme
  const setTheme = useCallback(
    (newPref: Theme | 'system') => {
      setPreference(newPref);
      localStorage.setItem('apex-theme-preference', newPref);
    },
    []
  );

  // Toggle theme
  const toggleTheme = useCallback(() => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  }, [theme, setTheme]);

  return {
    theme,
    isDark: theme === 'dark',
    setTheme,
    toggleTheme,
  };
}
