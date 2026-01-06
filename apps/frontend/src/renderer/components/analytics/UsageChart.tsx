/**
 * APEX Development Platform - Usage Chart
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import type { AnalyticsData } from './AnalyticsView';

/** Usage chart props */
export interface UsageChartProps {
  data: AnalyticsData['usage'];
}

/** Metric to display */
type UsageMetric = 'tokens' | 'tasks' | 'agentRuns';

const metricLabels: Record<UsageMetric, { label: string; color: string }> = {
  tokens: { label: 'Tokens', color: '#f59e0b' },
  tasks: { label: 'Tasks', color: '#3b82f6' },
  agentRuns: { label: 'Agent Runs', color: '#8b5cf6' },
};

/**
 * Usage Chart Component
 */
export const UsageChart: React.FC<UsageChartProps> = ({ data }) => {
  const [metric, setMetric] = useState<UsageMetric>('tokens');

  // Get max value for scaling
  const maxValue = Math.max(...data.map((d) => d[metric]), 1);

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  return (
    <div className="apex-usage-chart">
      <div className="apex-usage-chart__header">
        <h4>📈 Usage Over Time</h4>
        <div className="apex-usage-chart__metrics">
          {(Object.entries(metricLabels) as [UsageMetric, typeof metricLabels.tokens][]).map(
            ([key, { label, color }]) => (
              <button
                key={key}
                className={`apex-usage-chart__metric-btn ${
                  metric === key ? 'apex-usage-chart__metric-btn--active' : ''
                }`}
                style={{ borderColor: metric === key ? color : 'transparent' }}
                onClick={() => setMetric(key)}
              >
                {label}
              </button>
            )
          )}
        </div>
      </div>

      <div className="apex-usage-chart__content">
        <div className="apex-usage-chart__bars">
          {data.map((point) => {
            const height = (point[metric] / maxValue) * 100;
            return (
              <div key={point.date} className="apex-usage-chart__bar-container">
                <div
                  className="apex-usage-chart__bar"
                  style={{
                    height: `${height}%`,
                    backgroundColor: metricLabels[metric].color,
                  }}
                  title={`${formatDate(point.date)}: ${point[metric].toLocaleString()}`}
                />
                <span className="apex-usage-chart__date">
                  {formatDate(point.date)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="apex-usage-chart__footer">
        <span>Total: {data.reduce((sum, d) => sum + d[metric], 0).toLocaleString()}</span>
        <span>
          Avg: {Math.round(data.reduce((sum, d) => sum + d[metric], 0) / data.length).toLocaleString()}
        </span>
      </div>
    </div>
  );
};
