/**
 * APEX Development Platform - useDebounce Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Debounce Hook - Debounce a value
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Debounced Callback Hook - Debounce a callback function
 */
export function useDebouncedCallback<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number
): {
  debouncedCallback: (...args: Parameters<T>) => void;
  cancel: () => void;
  flush: () => void;
  isPending: () => boolean;
} {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingArgsRef = useRef<Parameters<T> | null>(null);
  const callbackRef = useRef(callback);

  // Keep callback ref up to date
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Cancel pending call
  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingArgsRef.current = null;
  }, []);

  // Flush pending call immediately
  const flush = useCallback(() => {
    if (timeoutRef.current && pendingArgsRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
      callbackRef.current(...pendingArgsRef.current);
      pendingArgsRef.current = null;
    }
  }, []);

  // Check if a call is pending
  const isPending = useCallback(() => {
    return timeoutRef.current !== null;
  }, []);

  // Debounced callback
  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      // Cancel any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Store pending args
      pendingArgsRef.current = args;

      // Set new timeout
      timeoutRef.current = setTimeout(() => {
        timeoutRef.current = null;
        callbackRef.current(...args);
        pendingArgsRef.current = null;
      }, delay);
    },
    [delay]
  );

  return {
    debouncedCallback,
    cancel,
    flush,
    isPending,
  };
}

/**
 * Throttle Hook - Throttle a callback function
 */
export function useThrottle<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const lastCallRef = useRef<number>(0);
  const callbackRef = useRef(callback);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCallRef.current >= delay) {
        lastCallRef.current = now;
        callbackRef.current(...args);
      }
    },
    [delay]
  );
}
