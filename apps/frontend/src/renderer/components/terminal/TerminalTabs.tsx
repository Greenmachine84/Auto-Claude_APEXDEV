/**
 * APEX Development Platform - Terminal Tabs
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import type { TerminalSession } from './TerminalView';

/** Terminal tabs props */
export interface TerminalTabsProps {
  sessions: TerminalSession[];
  activeSessionId: string | null;
  onSelect: (sessionId: string) => void;
  onClose: (sessionId: string) => void;
  onRename: (sessionId: string, name: string) => void;
  onNew: () => void;
  compact?: boolean;
}

/**
 * Terminal Tabs Component
 */
export const TerminalTabs: React.FC<TerminalTabsProps> = ({
  sessions,
  activeSessionId,
  onSelect,
  onClose,
  onRename,
  onNew,
  compact = false,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  // Start editing tab name
  const startEditing = (session: TerminalSession) => {
    setEditingId(session.id);
    setEditValue(session.name);
  };

  // Save edited name
  const saveEdit = () => {
    if (editingId && editValue.trim()) {
      onRename(editingId, editValue.trim());
    }
    setEditingId(null);
    setEditValue('');
  };

  // Handle key press in edit mode
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      saveEdit();
    } else if (e.key === 'Escape') {
      setEditingId(null);
      setEditValue('');
    }
  };

  return (
    <div className={`apex-terminal-tabs ${compact ? 'apex-terminal-tabs--compact' : ''}`}>
      <div className="apex-terminal-tabs__list">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`apex-terminal-tabs__tab ${
              session.id === activeSessionId ? 'apex-terminal-tabs__tab--active' : ''
            }`}
            onClick={() => onSelect(session.id)}
            onDoubleClick={() => startEditing(session)}
          >
            {editingId === session.id ? (
              <input
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onBlur={saveEdit}
                onKeyDown={handleKeyDown}
                className="apex-terminal-tabs__edit"
                autoFocus
              />
            ) : (
              <>
                <span className="apex-terminal-tabs__icon">
                  {session.agentId ? '🤖' : '🖥️'}
                </span>
                <span className="apex-terminal-tabs__name">{session.name}</span>
              </>
            )}
            <button
              className="apex-terminal-tabs__close"
              onClick={(e) => {
                e.stopPropagation();
                onClose(session.id);
              }}
              aria-label={`Close ${session.name}`}
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <button
        className="apex-terminal-tabs__new"
        onClick={onNew}
        aria-label="New terminal"
        title="New terminal (Ctrl+Shift+T)"
      >
        +
      </button>
    </div>
  );
};
