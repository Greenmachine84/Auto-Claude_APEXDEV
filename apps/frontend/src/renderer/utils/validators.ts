/**
 * APEX Development Platform - Validation Utilities
 * Phase 4: UI, Integrations & Analytics
 */

/** Validation result */
export interface ValidationResult {
  valid: boolean;
  error?: string;
}

/** Validation rule */
export type ValidationRule<T> = (value: T) => ValidationResult;

/**
 * Compose multiple validation rules
 */
export function composeValidators<T>(
  ...rules: ValidationRule<T>[]
): ValidationRule<T> {
  return (value: T) => {
    for (const rule of rules) {
      const result = rule(value);
      if (!result.valid) return result;
    }
    return { valid: true };
  };
}

/**
 * Required field validator
 */
export function required(message = 'This field is required'): ValidationRule<unknown> {
  return (value) => {
    if (value === null || value === undefined || value === '') {
      return { valid: false, error: message };
    }
    if (Array.isArray(value) && value.length === 0) {
      return { valid: false, error: message };
    }
    return { valid: true };
  };
}

/**
 * Minimum length validator
 */
export function minLength(
  min: number,
  message = `Must be at least ${min} characters`
): ValidationRule<string> {
  return (value) => {
    if (value.length < min) {
      return { valid: false, error: message };
    }
    return { valid: true };
  };
}

/**
 * Maximum length validator
 */
export function maxLength(
  max: number,
  message = `Must be at most ${max} characters`
): ValidationRule<string> {
  return (value) => {
    if (value.length > max) {
      return { valid: false, error: message };
    }
    return { valid: true };
  };
}

/**
 * Pattern validator
 */
export function pattern(
  regex: RegExp,
  message = 'Invalid format'
): ValidationRule<string> {
  return (value) => {
    if (!regex.test(value)) {
      return { valid: false, error: message };
    }
    return { valid: true };
  };
}

/**
 * Email validator
 */
export function email(message = 'Invalid email address'): ValidationRule<string> {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern(emailRegex, message);
}

/**
 * URL validator
 */
export function url(message = 'Invalid URL'): ValidationRule<string> {
  return (value) => {
    try {
      new URL(value);
      return { valid: true };
    } catch {
      return { valid: false, error: message };
    }
  };
}

/**
 * Number range validator
 */
export function range(
  min: number,
  max: number,
  message = `Must be between ${min} and ${max}`
): ValidationRule<number> {
  return (value) => {
    if (value < min || value > max) {
      return { valid: false, error: message };
    }
    return { valid: true };
  };
}

/**
 * Custom validator
 */
export function custom<T>(
  fn: (value: T) => boolean,
  message: string
): ValidationRule<T> {
  return (value) => {
    if (!fn(value)) {
      return { valid: false, error: message };
    }
    return { valid: true };
  };
}

/**
 * Validate object against schema
 */
export function validateObject<T extends Record<string, unknown>>(
  obj: T,
  schema: { [K in keyof T]?: ValidationRule<T[K]> }
): { valid: boolean; errors: Partial<Record<keyof T, string>> } {
  const errors: Partial<Record<keyof T, string>> = {};
  let valid = true;

  for (const key in schema) {
    const rule = schema[key];
    if (rule) {
      const result = rule(obj[key]);
      if (!result.valid) {
        valid = false;
        errors[key] = result.error;
      }
    }
  }

  return { valid, errors };
}

/**
 * API key format validators
 */
export const apiKeyValidators = {
  openai: pattern(/^sk-[a-zA-Z0-9-_]{32,}$/, 'Invalid OpenAI API key format'),
  anthropic: pattern(/^sk-ant-[a-zA-Z0-9-_]{32,}$/, 'Invalid Anthropic API key format'),
  github: pattern(/^ghp_[a-zA-Z0-9]{36}$|^github_pat_[a-zA-Z0-9_]{22}_[a-zA-Z0-9]{59}$/, 'Invalid GitHub token format'),
  gitlab: pattern(/^glpat-[a-zA-Z0-9-_]{20,}$/, 'Invalid GitLab token format'),
  linear: pattern(/^lin_api_[a-zA-Z0-9]{32}$/, 'Invalid Linear API key format'),
};
