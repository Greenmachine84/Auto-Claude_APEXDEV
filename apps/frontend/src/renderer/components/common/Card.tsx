/**
 * APEX Development Platform - Card Component
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';

/** Card props */
export interface CardProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  padding?: 'none' | 'small' | 'medium' | 'large';
  hoverable?: boolean;
  selected?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

/**
 * Card Component
 */
export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  actions,
  footer,
  className = '',
  padding = 'medium',
  hoverable = false,
  selected = false,
  onClick,
  children,
}) => {
  const classes = [
    'apex-card',
    `apex-card--padding-${padding}`,
    hoverable && 'apex-card--hoverable',
    selected && 'apex-card--selected',
    onClick && 'apex-card--clickable',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classes} onClick={onClick} role={onClick ? 'button' : undefined}>
      {(title || actions) && (
        <div className="apex-card__header">
          <div className="apex-card__header-text">
            {title && <h3 className="apex-card__title">{title}</h3>}
            {subtitle && <p className="apex-card__subtitle">{subtitle}</p>}
          </div>
          {actions && <div className="apex-card__actions">{actions}</div>}
        </div>
      )}
      <div className="apex-card__content">{children}</div>
      {footer && <div className="apex-card__footer">{footer}</div>}
    </div>
  );
};
