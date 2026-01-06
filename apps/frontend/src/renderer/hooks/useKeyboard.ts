/**
 * APEX Development Platform - useKeyboard Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useEffect, useCallback, useRef } from 'react';

/** Keyboard shortcut options */
export interface UseKeyboardOptions {
  /** Key combination (e.g., 'ctrl+k', 'shift+enter') */
  key: string;
  /** Handler function */
  handler: (event: KeyboardEvent) => void;
  /** Whether to prevent default behavior */
  preventDefault?: boolean;
  /** Whether shortcut is enabled */
  enabled?: boolean;
  /** Scope - only trigger within specific element */
  scope?: 'global' | 'focused';
}

/** Parse key combination */
function parseKey(key: string): {
  key: string;
  ctrl: boolean;
  shift: boolean;
  alt: boolean;
  meta: boolean;
} {
  const parts = key.toLowerCase().split('+');
  const mainKey = parts[parts.length - 1];
  
  return {
    key: mainKey,
    ctrl: parts.includes('ctrl') || parts.includes('control'),
    shift: parts.includes('shift'),
    alt: parts.includes('alt'),
    meta: parts.includes('meta') || parts.includes('cmd'),
  };
}

/** Check if key event matches combination */
function matchesKey(
  event: KeyboardEvent,
  parsed: ReturnType<typeof parseKey>
): boolean {
  const eventKey = event.key.toLowerCase();
  
  // Handle special keys
  const keyMatch =
    eventKey === parsed.key ||
    (parsed.key === 'enter' && eventKey === 'enter') ||
    (parsed.key === 'escape' && eventKey === 'escape') ||
    (parsed.key === 'tab' && eventKey === 'tab') ||
    (parsed.key === 'space' && eventKey === ' ') ||
    (parsed.key === 'backspace' && eventKey === 'backspace');

  return (
    keyMatch &&
    event.ctrlKey === parsed.ctrl &&
    event.shiftKey === parsed.shift &&
    event.altKey === parsed.alt &&
    event.metaKey === parsed.meta
  );
}

/**
 * Keyboard Hook - Handle keyboard shortcuts
 */
export function useKeyboard(options: UseKeyboardOptions): void {
  const { key, handler, preventDefault = true, enabled = true, scope = 'global' } = options;
  const parsedKey = useRef(parseKey(key));

  // Update parsed key when key changes
  useEffect(() => {
    parsedKey.current = parseKey(key);
  }, [key]);

  // Memoized handler
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Check scope
      if (scope === 'focused') {
        const activeElement = document.activeElement;
        if (
          activeElement instanceof HTMLInputElement ||
          activeElement instanceof HTMLTextAreaElement ||
          activeElement?.getAttribute('contenteditable') === 'true'
        ) {
          return;
        }
      }

      // Check if matches
      if (matchesKey(event, parsedKey.current)) {
        if (preventDefault) {
          event.preventDefault();
        }
        handler(event);
      }
    },
    [enabled, scope, preventDefault, handler]
  );

  // Attach listener
  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);
}

/**
 * Multiple keyboard shortcuts hook
 */
export function useKeyboardShortcuts(
  shortcuts: UseKeyboardOptions[]
): void {
  useEffect(() => {
    const handlers: ((event: KeyboardEvent) => void)[] = [];

    shortcuts.forEach(({ key, handler, preventDefault = true, enabled = true, scope = 'global' }) => {
      if (!enabled) return;

      const parsed = parseKey(key);
      const keyHandler = (event: KeyboardEvent) => {
        // Check scope
        if (scope === 'focused') {
          const activeElement = document.activeElement;
          if (
            activeElement instanceof HTMLInputElement ||
            activeElement instanceof HTMLTextAreaElement ||
            activeElement?.getAttribute('contenteditable') === 'true'
          ) {
            return;
          }
        }

        if (matchesKey(event, parsed)) {
          if (preventDefault) {
            event.preventDefault();
          }
          handler(event);
        }
      };

      handlers.push(keyHandler);
      window.addEventListener('keydown', keyHandler);
    });

    return () => {
      handlers.forEach((handler) => {
        window.removeEventListener('keydown', handler);
      });
    };
  }, [shortcuts]);
}
