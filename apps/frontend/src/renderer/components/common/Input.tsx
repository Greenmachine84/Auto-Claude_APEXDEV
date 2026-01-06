/**
 * APEX Development Platform - Input Component
 * Phase 4: UI, Integrations & Analytics
 */

import React, { forwardRef } from 'react';

/** Input props */
export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  hint?: string;
  size?: 'small' | 'medium' | 'large';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

/**
 * Input Component
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      hint,
      size = 'medium',
      leftIcon,
      rightIcon,
      fullWidth = false,
      className = '',
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).slice(2, 9)}`;

    const wrapperClasses = [
      'apex-input-wrapper',
      fullWidth && 'apex-input-wrapper--full-width',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    const inputClasses = [
      'apex-input',
      `apex-input--${size}`,
      error && 'apex-input--error',
      leftIcon && 'apex-input--has-left-icon',
      rightIcon && 'apex-input--has-right-icon',
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={wrapperClasses}>
        {label && (
          <label htmlFor={inputId} className="apex-input__label">
            {label}
          </label>
        )}
        <div className="apex-input__container">
          {leftIcon && <span className="apex-input__icon apex-input__icon--left">{leftIcon}</span>}
          <input ref={ref} id={inputId} className={inputClasses} {...props} />
          {rightIcon && (
            <span className="apex-input__icon apex-input__icon--right">{rightIcon}</span>
          )}
        </div>
        {error && <span className="apex-input__error">{error}</span>}
        {hint && !error && <span className="apex-input__hint">{hint}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
