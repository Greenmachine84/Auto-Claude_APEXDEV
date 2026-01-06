/**
 * APEX Development Platform - Agent Card
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { Agent } from '../../../preload/api/agent-api';

/** Status colors */
const statusColors: Record<string, string> = {
  idle: '#6b7280',
  running: '#22c55e',
  paused: '#f59e0b',
  error: '#ef4444',
  stopped: '#9ca3af',
};

/** Agent type icons */
const typeIcons: Record<string, string> = {
  coder: '💻',
  reviewer: '🔍',
  fixer: '🛠️',
  planner: '📝',
  analyst: '📊',
};

/** Agent card props */
export interface AgentCardProps {
  agent: Agent;
  isSelected?: boolean;
  onClick: () => void;
  onStop: () => void;
}

/**
 * Agent Card Component
 */
export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  isSelected,
  onClick,
  onStop,
}) => {
  const formatDuration = (start?: string) => {
    if (!start) return '--';
    const ms = Date.now() - new Date(start).getTime();
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const isRunning = agent.status === 'running';

  return (
    <div
      className={`apex-agent-card ${isSelected ? 'apex-agent-card--selected' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {/* Status Indicator */}
      <div
        className="apex-agent-card__status-indicator"
        style={{ backgroundColor: statusColors[agent.status] }}
        title={agent.status}
      />

      {/* Agent Info */}
      <div className="apex-agent-card__info">
        <div className="apex-agent-card__header">
          <span className="apex-agent-card__icon">
            {typeIcons[agent.type] || '🤖'}
          </span>
          <span className="apex-agent-card__type">{agent.type}</span>
          <span className="apex-agent-card__id" title={agent.id}>
            {agent.id.slice(0, 8)}
          </span>
        </div>

        <div className="apex-agent-card__stats">
          <span className="apex-agent-card__stat">
            <span className="apex-agent-card__stat-label">Status:</span>
            <span
              className="apex-agent-card__stat-value"
              style={{ color: statusColors[agent.status] }}
            >
              {agent.status}
            </span>
          </span>
          {agent.startedAt && (
            <span className="apex-agent-card__stat">
              <span className="apex-agent-card__stat-label">Uptime:</span>
              <span className="apex-agent-card__stat-value">
                {formatDuration(agent.startedAt)}
              </span>
            </span>
          )}
          {agent.taskId && (
            <span className="apex-agent-card__stat">
              <span className="apex-agent-card__stat-label">Task:</span>
              <span className="apex-agent-card__stat-value">
                {agent.taskId.slice(0, 8)}
              </span>
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="apex-agent-card__actions">
        {isRunning && (
          <button
            className="apex-agent-card__stop-btn"
            onClick={(e) => {
              e.stopPropagation();
              onStop();
            }}
            title="Stop agent"
          >
            ⏹
          </button>
        )}
      </div>
    </div>
  );
};
