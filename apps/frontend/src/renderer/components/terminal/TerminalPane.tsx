/**
 * APEX Development Platform - Terminal Pane
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useEffect, useRef } from 'react';
import type { TerminalSession } from './TerminalView';

/** Terminal pane props */
export interface TerminalPaneProps {
  session: TerminalSession;
  isActive: boolean;
  onFocus: () => void;
}

/**
 * Terminal Pane Component
 *
 * Note: This is a placeholder that would integrate with xterm.js
 * or a similar terminal emulator in a real implementation.
 */
export const TerminalPane: React.FC<TerminalPaneProps> = ({
  session,
  isActive,
  onFocus,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const terminalRef = useRef<unknown>(null);

  // Initialize terminal
  useEffect(() => {
    if (!containerRef.current) return;

    // In a real implementation, we would initialize xterm.js here:
    // const terminal = new Terminal({ ... });
    // terminal.open(containerRef.current);
    // terminalRef.current = terminal;

    // For now, we'll just log initialization
    console.log(`Terminal initialized for session: ${session.id}`);

    return () => {
      // Cleanup terminal
      if (terminalRef.current) {
        // terminal.dispose();
      }
    };
  }, [session.id]);

  // Focus terminal when active
  useEffect(() => {
    if (isActive && terminalRef.current) {
      // terminal.focus();
    }
  }, [isActive]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (terminalRef.current) {
        // terminal.fit();
      }
    };

    const resizeObserver = new ResizeObserver(handleResize);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => resizeObserver.disconnect();
  }, []);

  return (
    <div
      className={`apex-terminal-pane ${isActive ? 'apex-terminal-pane--active' : ''}`}
      onClick={onFocus}
    >
      {/* Terminal Header */}
      <div className="apex-terminal-pane__header">
        <span className="apex-terminal-pane__name">{session.name}</span>
        <span className="apex-terminal-pane__cwd" title={session.cwd}>
          {session.cwd.split('/').pop() || session.cwd}
        </span>
        {session.agentId && (
          <span className="apex-terminal-pane__agent" title={`Agent: ${session.agentId}`}>
            🤖
          </span>
        )}
      </div>

      {/* Terminal Container */}
      <div
        ref={containerRef}
        className="apex-terminal-pane__terminal"
        data-session-id={session.id}
      >
        {/* xterm.js will render here */}
        <div className="apex-terminal-pane__placeholder">
          <pre>
            {`APEX Terminal - ${session.name}
$ _`}
          </pre>
        </div>
      </div>
    </div>
  );
};
