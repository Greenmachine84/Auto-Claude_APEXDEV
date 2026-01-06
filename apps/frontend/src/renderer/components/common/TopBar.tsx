/**
 * APEX Development Platform - Top Bar Component
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { ViewType } from '../../App';

/** Top bar props */
export interface TopBarProps {
  currentView: ViewType;
  onMenuClick: () => void;
  onSettingsClick: () => void;
}

/** View titles */
const viewTitles: Record<ViewType, string> = {
  kanban: 'Task Board',
  terminal: 'Terminal',
  agents: 'AI Agents',
  memory: 'Episodic Memory',
  workflow: 'Workflows',
  settings: 'Settings',
  analytics: 'Analytics Dashboard',
};

/**
 * Top Bar Component
 */
export const TopBar: React.FC<TopBarProps> = ({ currentView, onMenuClick, onSettingsClick }) => {
  const isMac = window.apex.platform.isMac;

  return (
    <header className={`apex-topbar ${isMac ? 'apex-topbar--mac' : ''}`}>
      {/* Drag region for window dragging */}
      <div className="apex-topbar__drag-region" />

      {/* Left section */}
      <div className="apex-topbar__left">
        <button
          className="apex-topbar__menu-btn"
          onClick={onMenuClick}
          aria-label="Toggle sidebar"
        >
          ☰
        </button>
        <h1 className="apex-topbar__title">{viewTitles[currentView]}</h1>
      </div>

      {/* Center section - breadcrumbs or search */}
      <div className="apex-topbar__center">
        <div className="apex-topbar__search">
          <input
            type="text"
            placeholder="Search tasks, agents, memory..."
            className="apex-topbar__search-input"
          />
          <span className="apex-topbar__search-shortcut">Cmd+K</span>
        </div>
      </div>

      {/* Right section */}
      <div className="apex-topbar__right">
        <button className="apex-topbar__icon-btn" title="Notifications">
          🔔
        </button>
        <button className="apex-topbar__icon-btn" title="Help">
          ❓
        </button>
        <button
          className="apex-topbar__icon-btn"
          onClick={onSettingsClick}
          title="Settings"
        >
          ⚙️
        </button>
      </div>

      {/* Window controls (Windows/Linux only) */}
      {!isMac && (
        <div className="apex-topbar__window-controls">
          <button
            className="apex-topbar__window-btn apex-topbar__window-btn--minimize"
            onClick={() => window.apex.window.minimize()}
            aria-label="Minimize"
          >
            —
          </button>
          <button
            className="apex-topbar__window-btn apex-topbar__window-btn--maximize"
            onClick={() => window.apex.window.maximize()}
            aria-label="Maximize"
          >
            □
          </button>
          <button
            className="apex-topbar__window-btn apex-topbar__window-btn--close"
            onClick={() => window.apex.window.close()}
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      )}
    </header>
  );
};
