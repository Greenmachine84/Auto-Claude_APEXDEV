/**
 * APEX Development Platform - Terminal View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { TerminalGrid } from './TerminalGrid';
import { TerminalTabs } from './TerminalTabs';
import { TerminalToolbar } from './TerminalToolbar';

/** Terminal session */
export interface TerminalSession {
  id: string;
  name: string;
  cwd: string;
  isActive: boolean;
  agentId?: string;
}

/** Terminal view props */
interface TerminalViewProps {
  embedded?: boolean;
}

/**
 * Terminal View Component
 */
const TerminalView: React.FC<TerminalViewProps> = ({ embedded = false }) => {
  const [sessions, setSessions] = useState<TerminalSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [layout, setLayout] = useState<'single' | 'split-h' | 'split-v' | 'grid'>('single');

  // Create new terminal session
  const createSession = useCallback(async (name?: string) => {
    const session: TerminalSession = {
      id: `term-${Date.now()}`,
      name: name || `Terminal ${sessions.length + 1}`,
      cwd: process.cwd(),
      isActive: true,
    };

    setSessions((prev) => [...prev, session]);
    setActiveSessionId(session.id);
    return session;
  }, [sessions.length]);

  // Close terminal session
  const closeSession = useCallback((sessionId: string) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== sessionId);
      if (activeSessionId === sessionId && updated.length > 0) {
        setActiveSessionId(updated[updated.length - 1].id);
      } else if (updated.length === 0) {
        setActiveSessionId(null);
      }
      return updated;
    });
  }, [activeSessionId]);

  // Rename session
  const renameSession = useCallback((sessionId: string, name: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? { ...s, name } : s))
    );
  }, []);

  // Initialize with one terminal
  useEffect(() => {
    if (sessions.length === 0) {
      createSession('Main');
    }
  }, [sessions.length, createSession]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.shiftKey) {
        switch (e.key.toLowerCase()) {
          case 't':
            e.preventDefault();
            createSession();
            break;
          case 'w':
            e.preventDefault();
            if (activeSessionId) closeSession(activeSessionId);
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeSessionId, createSession, closeSession]);

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const visibleSessions = layout === 'single'
    ? activeSession
      ? [activeSession]
      : []
    : sessions.slice(0, layout === 'grid' ? 4 : 2);

  return (
    <div className={`apex-terminal-view ${embedded ? 'apex-terminal-view--embedded' : ''}`}>
      {/* Toolbar */}
      {!embedded && (
        <TerminalToolbar
          layout={layout}
          onLayoutChange={setLayout}
          onNewTerminal={() => createSession()}
          onClear={() => {
            if (activeSessionId) {
              window.apex.events.on('terminal:clear', () => {});
            }
          }}
        />
      )}

      {/* Tabs */}
      <TerminalTabs
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelect={setActiveSessionId}
        onClose={closeSession}
        onRename={renameSession}
        onNew={() => createSession()}
        compact={embedded}
      />

      {/* Terminal Grid */}
      <TerminalGrid
        sessions={visibleSessions}
        activeSessionId={activeSessionId}
        layout={layout}
        onSessionSelect={setActiveSessionId}
      />
    </div>
  );
};

export default TerminalView;
