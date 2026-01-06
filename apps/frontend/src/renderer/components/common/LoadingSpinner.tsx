/**
 * APEX Development Platform - Loading Spinner
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';

/** Loading spinner props */
export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  label?: string;
  className?: string;
}

/**
 * Loading Spinner Component
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color,
  label,
  className = '',
}) => {
  const sizeMap = {
    small: 16,
    medium: 32,
    large: 48,
  };

  const spinnerSize = sizeMap[size];

  return (
    <div
      className={`apex-loading-spinner apex-loading-spinner--${size} ${className}`}
      role="status"
      aria-label={label || 'Loading'}
    >
      <svg
        width={spinnerSize}
        height={spinnerSize}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          className="apex-loading-spinner__track"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="3"
          opacity="0.2"
        />
        <path
          className="apex-loading-spinner__arc"
          d="M12 2C6.48 2 2 6.48 2 12"
          stroke={color || 'currentColor'}
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      {label && <span className="apex-loading-spinner__label">{label}</span>}
    </div>
  );
};
