/**
 * APEX Development Platform - Agent Logs
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useRef, useEffect } from 'react';

/** Agent logs props */
export interface AgentLogsProps {
  logs: string[] | import('../../../preload/api/agent-api').AgentLog[];
  agentId: string;
}

/**
 * Agent Logs Component
 */
export const AgentLogs: React.FC<AgentLogsProps> = ({ logs, agentId }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const autoScrollRef = useRef(true);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScrollRef.current && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 50;
  };

  // Parse log level from log string
  const getLogLevel = (log: string | import('../../../preload/api/agent-api').AgentLog): string => {
    if (typeof log !== 'string') return log.level || 'info';
    if (log.includes('[ERROR]') || log.includes('ERROR:')) return 'error';
    if (log.includes('[WARN]') || log.includes('WARNING:')) return 'warn';
    if (log.includes('[DEBUG]') || log.includes('DEBUG:')) return 'debug';
    return 'info';
  };

  // Copy logs to clipboard
  const handleCopyLogs = () => {
    const text = logs.map((l: string | import('../../../preload/api/agent-api').AgentLog) => typeof l === 'string' ? l : l.message).join('\n');
    navigator.clipboard.writeText(text);
  };

  // Clear logs display
  const handleClear = () => {
    // This would need to be connected to actual clear functionality
    console.log('Clear logs for agent:', agentId);
  };

  return (
    <div className="apex-agent-logs">
      {/* Toolbar */}
      <div className="apex-agent-logs__toolbar">
        <span className="apex-agent-logs__count">{logs.length} entries</span>
        <div className="apex-agent-logs__actions">
          <button
            className="apex-agent-logs__btn"
            onClick={handleCopyLogs}
            title="Copy logs"
          >
            📋 Copy
          </button>
          <button
            className="apex-agent-logs__btn"
            onClick={handleClear}
            title="Clear logs"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      {/* Log Container */}
      <div
        ref={containerRef}
        className="apex-agent-logs__container"
        onScroll={handleScroll}
      >
        {logs.length === 0 ? (
          <div className="apex-agent-logs__empty">No logs available</div>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              className={`apex-agent-logs__entry apex-agent-logs__entry--${getLogLevel(log)}`}
            >
              <span className="apex-agent-logs__line-num">{index + 1}</span>
              <span className="apex-agent-logs__text">{typeof log === "string" ? log : log.message}</span>
            </div>
          ))
        )}
      </div>

      {/* Auto-scroll indicator */}
      {!autoScrollRef.current && logs.length > 0 && (
        <button
          className="apex-agent-logs__scroll-btn"
          onClick={() => {
            autoScrollRef.current = true;
            if (containerRef.current) {
              containerRef.current.scrollTop = containerRef.current.scrollHeight;
            }
          }}
        >
          ↓ Scroll to bottom
        </button>
      )}
    </div>
  );
};


