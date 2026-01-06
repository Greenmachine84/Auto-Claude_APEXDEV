/**
 * APEX Development Platform - Agent Performance
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { AnalyticsData } from './AnalyticsView';

/** Agent performance props */
export interface AgentPerformanceProps {
  data: AnalyticsData['agentPerformance'];
}

/** Agent type icons */
const agentIcons: Record<string, string> = {
  coder: '💻',
  reviewer: '🔍',
  fixer: '🔧',
  planner: '📝',
  analyst: '📊',
};

/**
 * Agent Performance Component
 */
export const AgentPerformance: React.FC<AgentPerformanceProps> = ({ data }) => {
  // Sort by runs descending
  const sortedData = [...data].sort((a, b) => b.runs - a.runs);

  // Format duration
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  };

  // Get success rate color
  const getSuccessRateColor = (rate: number) => {
    if (rate >= 0.9) return '#22c55e';
    if (rate >= 0.7) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="apex-agent-performance">
      <div className="apex-agent-performance__header">
        <h4>🤖 Agent Performance</h4>
      </div>

      <div className="apex-agent-performance__table">
        <div className="apex-agent-performance__row apex-agent-performance__row--header">
          <span>Agent</span>
          <span>Runs</span>
          <span>Success</span>
          <span>Avg Time</span>
          <span>Tokens</span>
        </div>

        {sortedData.map((agent) => (
          <div key={agent.agentType} className="apex-agent-performance__row">
            <span className="apex-agent-performance__name">
              <span className="apex-agent-performance__icon">
                {agentIcons[agent.agentType] || '🤖'}
              </span>
              {agent.agentType}
            </span>
            <span>{agent.runs.toLocaleString()}</span>
            <span
              className="apex-agent-performance__success"
              style={{ color: getSuccessRateColor(agent.successRate) }}
            >
              {(agent.successRate * 100).toFixed(0)}%
            </span>
            <span>{formatDuration(agent.avgDuration)}</span>
            <span>
              {agent.tokensUsed >= 1000
                ? `${(agent.tokensUsed / 1000).toFixed(0)}K`
                : agent.tokensUsed}
            </span>
          </div>
        ))}
      </div>

      <div className="apex-agent-performance__footer">
        <span>
          Total Runs: {data.reduce((sum, a) => sum + a.runs, 0).toLocaleString()}
        </span>
        <span>
          Avg Success:{' '}
          {(
            data.reduce((sum, a) => sum + a.successRate * a.runs, 0) /
            data.reduce((sum, a) => sum + a.runs, 0) *
            100
          ).toFixed(1)}%
        </span>
      </div>
    </div>
  );
};
