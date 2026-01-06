/**
 * APEX Development Platform - Terminal Grid
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { TerminalPane } from './TerminalPane';
import type { TerminalSession } from './TerminalView';

/** Layout type */
export type TerminalLayout = 'single' | 'split-h' | 'split-v' | 'grid';

/** Terminal grid props */
export interface TerminalGridProps {
  sessions: TerminalSession[];
  activeSessionId: string | null;
  layout: TerminalLayout;
  onSessionSelect: (sessionId: string) => void;
}

/**
 * Terminal Grid Component
 */
export const TerminalGrid: React.FC<TerminalGridProps> = ({
  sessions,
  activeSessionId,
  layout,
  onSessionSelect,
}) => {
  if (sessions.length === 0) {
    return (
      <div className="apex-terminal-grid apex-terminal-grid--empty">
        <p>No terminal sessions</p>
        <p>Press Ctrl+Shift+T to create one</p>
      </div>
    );
  }

  const gridClass = `apex-terminal-grid apex-terminal-grid--${layout}`;

  return (
    <div className={gridClass}>
      {sessions.map((session) => (
        <TerminalPane
          key={session.id}
          session={session}
          isActive={session.id === activeSessionId}
          onFocus={() => onSessionSelect(session.id)}
        />
      ))}
    </div>
  );
};
