/**
 * APEX Development Platform - Button Component
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';

/** Button variants */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';

/** Button sizes */
export type ButtonSize = 'small' | 'medium' | 'large';

/** Button props */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

/**
 * Button Component
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  disabled,
  children,
  className = '',
  ...props
}) => {
  const classes = [
    'apex-button',
    `apex-button--${variant}`,
    `apex-button--${size}`,
    fullWidth && 'apex-button--full-width',
    loading && 'apex-button--loading',
    disabled && 'apex-button--disabled',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} disabled={disabled || loading} {...props}>
      {loading && <span className="apex-button__spinner" />}
      {!loading && icon && iconPosition === 'left' && (
        <span className="apex-button__icon apex-button__icon--left">{icon}</span>
      )}
      <span className="apex-button__content">{children}</span>
      {!loading && icon && iconPosition === 'right' && (
        <span className="apex-button__icon apex-button__icon--right">{icon}</span>
      )}
    </button>
  );
};
