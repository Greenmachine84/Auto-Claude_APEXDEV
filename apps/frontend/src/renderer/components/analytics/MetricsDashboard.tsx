/**
 * APEX Development Platform - Metrics Dashboard
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { AnalyticsData } from './AnalyticsView';

/** Metrics dashboard props */
export interface MetricsDashboardProps {
  summary: AnalyticsData['summary'];
}

/** Metric card config */
interface MetricCard {
  key: keyof AnalyticsData['summary'];
  icon: string;
  label: string;
  format: (value: number) => string;
  color: string;
}

const metricCards: MetricCard[] = [
  {
    key: 'totalTasks',
    icon: '📝',
    label: 'Total Tasks',
    format: (v) => v.toLocaleString(),
    color: '#3b82f6',
  },
  {
    key: 'completedTasks',
    icon: '✅',
    label: 'Completed',
    format: (v) => v.toLocaleString(),
    color: '#22c55e',
  },
  {
    key: 'totalAgentRuns',
    icon: '🤖',
    label: 'Agent Runs',
    format: (v) => v.toLocaleString(),
    color: '#8b5cf6',
  },
  {
    key: 'totalTokensUsed',
    icon: '💬',
    label: 'Tokens Used',
    format: (v) => (v >= 1000000 ? `${(v / 1000000).toFixed(1)}M` : `${(v / 1000).toFixed(0)}K`),
    color: '#f59e0b',
  },
  {
    key: 'estimatedCost',
    icon: '💰',
    label: 'Est. Cost',
    format: (v) => `$${v.toFixed(2)}`,
    color: '#ec4899',
  },
  {
    key: 'averageTaskDuration',
    icon: '⏱️',
    label: 'Avg Duration',
    format: (v) => `${Math.floor(v / 60)}m ${Math.floor(v % 60)}s`,
    color: '#14b8a6',
  },
];

/**
 * Metrics Dashboard Component
 */
export const MetricsDashboard: React.FC<MetricsDashboardProps> = ({ summary }) => {
  return (
    <div className="apex-metrics-dashboard">
      {metricCards.map(({ key, icon, label, format, color }) => (
        <div
          key={key}
          className="apex-metrics-dashboard__card"
          style={{ borderTopColor: color }}
        >
          <span className="apex-metrics-dashboard__icon">{icon}</span>
          <div className="apex-metrics-dashboard__content">
            <span className="apex-metrics-dashboard__value">
              {format(summary[key])}
            </span>
            <span className="apex-metrics-dashboard__label">{label}</span>
          </div>
        </div>
      ))}
    </div>
  );
};
