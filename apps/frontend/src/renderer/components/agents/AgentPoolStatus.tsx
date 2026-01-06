/**
 * APEX Development Platform - Agent Pool Status
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { AgentPoolStatus as PoolStatus } from '../../../preload/api/agent-api';

/** Agent pool status props */
export interface AgentPoolStatusProps {
  status: PoolStatus;
}

/** Agent type colors */
const typeColors: Record<string, string> = {
  coder: '#3b82f6',
  reviewer: '#8b5cf6',
  fixer: '#f59e0b',
  planner: '#22c55e',
  analyst: '#ec4899',
};

/**
 * Agent Pool Status Component
 */
export const AgentPoolStatus: React.FC<AgentPoolStatusProps> = ({ status }) => {
  const utilizationPercent = status.totalAgents > 0
    ? Math.round((status.runningAgents / status.totalAgents) * 100)
    : 0;

  return (
    <div className="apex-agent-pool-status">
      {/* Summary Stats */}
      <div className="apex-agent-pool-status__summary">
        <div className="apex-agent-pool-status__stat">
          <span className="apex-agent-pool-status__stat-value">
            {status.totalAgents}
          </span>
          <span className="apex-agent-pool-status__stat-label">Total Agents</span>
        </div>
        <div className="apex-agent-pool-status__stat">
          <span className="apex-agent-pool-status__stat-value apex-agent-pool-status__stat-value--running">
            {status.runningAgents}
          </span>
          <span className="apex-agent-pool-status__stat-label">Running</span>
        </div>
        <div className="apex-agent-pool-status__stat">
          <span className="apex-agent-pool-status__stat-value">
            {status.idleAgents}
          </span>
          <span className="apex-agent-pool-status__stat-label">Idle</span>
        </div>
        <div className="apex-agent-pool-status__stat">
          <span className="apex-agent-pool-status__stat-value">
            {status.queuedTasks}
          </span>
          <span className="apex-agent-pool-status__stat-label">Queued Tasks</span>
        </div>
      </div>

      {/* Utilization Bar */}
      <div className="apex-agent-pool-status__utilization">
        <div className="apex-agent-pool-status__utilization-header">
          <span>Pool Utilization</span>
          <span>{utilizationPercent}%</span>
        </div>
        <div className="apex-agent-pool-status__utilization-bar">
          <div
            className="apex-agent-pool-status__utilization-fill"
            style={{ width: `${utilizationPercent}%` }}
          />
        </div>
      </div>

      {/* Agents by Type */}
      <div className="apex-agent-pool-status__by-type">
        <h4>Agents by Type</h4>
        <div className="apex-agent-pool-status__type-grid">
          {Object.entries(status.agentsByType).map(([type, count]) => (
            <div key={type} className="apex-agent-pool-status__type">
              <span
                className="apex-agent-pool-status__type-indicator"
                style={{ backgroundColor: typeColors[type] || '#6b7280' }}
              />
              <span className="apex-agent-pool-status__type-name">{type}</span>
              <span className="apex-agent-pool-status__type-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
