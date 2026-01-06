/**
 * APEX Development Platform - Theme Configuration
 * Phase 4: UI, Integrations & Analytics
 */

/** Theme type */
export type Theme = 'light' | 'dark' | 'system';

/** Resolved theme (never 'system') */
export type ResolvedTheme = 'light' | 'dark';

/** Color token names */
export type ColorToken =
  | 'bg-primary'
  | 'bg-secondary'
  | 'bg-tertiary'
  | 'bg-hover'
  | 'bg-active'
  | 'text-primary'
  | 'text-secondary'
  | 'text-tertiary'
  | 'text-inverse'
  | 'border-primary'
  | 'border-secondary'
  | 'primary'
  | 'primary-hover'
  | 'primary-light'
  | 'success'
  | 'success-hover'
  | 'success-light'
  | 'warning'
  | 'warning-hover'
  | 'warning-light'
  | 'error'
  | 'error-hover'
  | 'error-light'
  | 'info'
  | 'info-hover'
  | 'info-light';

/** Get CSS variable for color */
export function getColor(token: ColorToken): string {
  return `var(--color-${token})`;
}

/** Space scale */
export type SpaceToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

/** Get CSS variable for spacing */
export function getSpace(token: SpaceToken): string {
  return `var(--space-${token})`;
}

/** Radius scale */
export type RadiusToken = 'sm' | 'md' | 'lg' | 'full';

/** Get CSS variable for radius */
export function getRadius(token: RadiusToken): string {
  return `var(--radius-${token})`;
}

/** Shadow scale */
export type ShadowToken = 'sm' | 'md' | 'lg' | 'xl';

/** Get CSS variable for shadow */
export function getShadow(token: ShadowToken): string {
  return `var(--shadow-${token})`;
}

/** Detect system theme preference */
export function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'dark';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/** Resolve theme (convert 'system' to actual theme) */
export function resolveTheme(theme: Theme): ResolvedTheme {
  return theme === 'system' ? getSystemTheme() : theme;
}

/** Apply theme to document */
export function applyTheme(theme: ResolvedTheme): void {
  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.classList.remove('theme-light', 'theme-dark');
  document.documentElement.classList.add(`theme-${theme}`);
}

/** Theme configuration */
export const themeConfig = {
  defaultTheme: 'system' as Theme,
  storageKey: 'apex-theme',
  themes: ['light', 'dark', 'system'] as const,
};
