/**
 * APEX Development Platform - Terminal Toolbar
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Button } from '../common/Button';
import type { TerminalLayout } from './TerminalGrid';

/** Terminal toolbar props */
export interface TerminalToolbarProps {
  layout: TerminalLayout;
  onLayoutChange: (layout: TerminalLayout) => void;
  onNewTerminal: () => void;
  onClear: () => void;
}

/** Layout options */
const layoutOptions: { id: TerminalLayout; icon: string; label: string }[] = [
  { id: 'single', icon: '□', label: 'Single' },
  { id: 'split-h', icon: '◫', label: 'Split Horizontal' },
  { id: 'split-v', icon: '⬜', label: 'Split Vertical' },
  { id: 'grid', icon: '⊞', label: 'Grid' },
];

/**
 * Terminal Toolbar Component
 */
export const TerminalToolbar: React.FC<TerminalToolbarProps> = ({
  layout,
  onLayoutChange,
  onNewTerminal,
  onClear,
}) => {
  return (
    <div className="apex-terminal-toolbar">
      <div className="apex-terminal-toolbar__left">
        <Button
          variant="ghost"
          size="small"
          onClick={onNewTerminal}
          title="New Terminal"
        >
          + New
        </Button>
        <Button variant="ghost" size="small" onClick={onClear} title="Clear">
          Clear
        </Button>
      </div>

      <div className="apex-terminal-toolbar__center">
        <span className="apex-terminal-toolbar__label">Layout:</span>
        <div className="apex-terminal-toolbar__layouts">
          {layoutOptions.map((option) => (
            <button
              key={option.id}
              className={`apex-terminal-toolbar__layout-btn ${
                layout === option.id ? 'apex-terminal-toolbar__layout-btn--active' : ''
              }`}
              onClick={() => onLayoutChange(option.id)}
              title={option.label}
              aria-label={option.label}
            >
              {option.icon}
            </button>
          ))}
        </div>
      </div>

      <div className="apex-terminal-toolbar__right">
        <Button variant="ghost" size="small" title="Settings">
          ⚙️
        </Button>
      </div>
    </div>
  );
};
