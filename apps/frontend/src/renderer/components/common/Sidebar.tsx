/**
 * APEX Development Platform - Sidebar Component
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { ViewType } from '../../App';

/** Sidebar props */
export interface SidebarProps {
  isOpen: boolean;
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
  onToggle: () => void;
}

/** Navigation item */
interface NavItem {
  id: ViewType;
  label: string;
  icon: string;
  badge?: number;
}

/** Navigation items */
const navItems: NavItem[] = [
  { id: 'kanban', label: 'Tasks', icon: '📋' },
  { id: 'agents', label: 'Agents', icon: '🤖' },
  { id: 'terminal', label: 'Terminal', icon: '🖥️' },
  { id: 'memory', label: 'Memory', icon: '🧠' },
  { id: 'workflow', label: 'Workflows', icon: '🔄' },
  { id: 'analytics', label: 'Analytics', icon: '📊' },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
];

/**
 * Sidebar Component
 */
export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  currentView,
  onViewChange,
  onToggle,
}) => {
  return (
    <aside className={`apex-sidebar ${isOpen ? 'apex-sidebar--open' : 'apex-sidebar--collapsed'}`}>
      {/* Logo */}
      <div className="apex-sidebar__header">
        <div className="apex-sidebar__logo">
          <span className="apex-sidebar__logo-icon">⚡</span>
          {isOpen && <span className="apex-sidebar__logo-text">APEX</span>}
        </div>
        <button
          className="apex-sidebar__toggle"
          onClick={onToggle}
          aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {isOpen ? '◀' : '▶'}
        </button>
      </div>

      {/* Navigation */}
      <nav className="apex-sidebar__nav">
        <ul className="apex-sidebar__nav-list">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                className={`apex-sidebar__nav-item ${
                  currentView === item.id ? 'apex-sidebar__nav-item--active' : ''
                }`}
                onClick={() => onViewChange(item.id)}
                title={isOpen ? undefined : item.label}
              >
                <span className="apex-sidebar__nav-icon">{item.icon}</span>
                {isOpen && <span className="apex-sidebar__nav-label">{item.label}</span>}
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="apex-sidebar__nav-badge">{item.badge}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="apex-sidebar__footer">
        {isOpen && (
          <div className="apex-sidebar__version">
            v{window.apex.platform.versions.electron}
          </div>
        )}
      </div>
    </aside>
  );
};
