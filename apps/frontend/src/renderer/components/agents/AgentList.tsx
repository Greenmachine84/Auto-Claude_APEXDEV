/**
 * APEX Development Platform - Agent List
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { AgentCard } from './AgentCard';
import { LoadingSpinner } from '../common/LoadingSpinner';
import type { Agent, AgentType } from '../../../preload/api/agent-api';

/** Agent list props */
export interface AgentListProps {
  agents: Agent[];
  selectedAgentId: string | null;
  loading?: boolean;
  onSelect: (agent: Agent) => void;
  onStart: (type: AgentType) => void;
  onStop: (agentId: string) => void;
}

/** Agent types for quick start */
const agentTypes: { type: AgentType; icon: string; label: string }[] = [
  { type: 'coder', icon: '💻', label: 'Coder' },
  { type: 'reviewer', icon: '🔍', label: 'Reviewer' },
  { type: 'fixer', icon: '🛠️', label: 'Fixer' },
  { type: 'planner', icon: '📝', label: 'Planner' },
  { type: 'analyst', icon: '📊', label: 'Analyst' },
];

/**
 * Agent List Component
 */
export const AgentList: React.FC<AgentListProps> = ({
  agents,
  selectedAgentId,
  loading,
  onSelect,
  onStart,
  onStop,
}) => {
  if (loading) {
    return (
      <div className="apex-agent-list apex-agent-list--loading">
        <LoadingSpinner label="Loading agents..." />
      </div>
    );
  }

  return (
    <div className="apex-agent-list">
      {/* Quick Start */}
      <div className="apex-agent-list__quick-start">
        <h3>Quick Start</h3>
        <div className="apex-agent-list__types">
          {agentTypes.map(({ type, icon, label }) => (
            <button
              key={type}
              className="apex-agent-list__type-btn"
              onClick={() => onStart(type)}
              title={`Start ${label} agent`}
            >
              <span className="apex-agent-list__type-icon">{icon}</span>
              <span className="apex-agent-list__type-label">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Agent Cards */}
      <div className="apex-agent-list__agents">
        <h3>Active Agents ({agents.length})</h3>
        {agents.length === 0 ? (
          <div className="apex-agent-list__empty">
            <p>No agents running</p>
            <p>Start an agent using the quick start buttons above</p>
          </div>
        ) : (
          <div className="apex-agent-list__cards">
            {agents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                isSelected={agent.id === selectedAgentId}
                onClick={() => onSelect(agent)}
                onStop={() => onStop(agent.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
