/**
 * APEX Development Platform - Task Metrics
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { AnalyticsData } from './AnalyticsView';

/** Task metrics props */
export interface TaskMetricsProps {
  data: AnalyticsData['taskMetrics'];
}

/** Status config */
const statusConfig: Record<string, { icon: string; color: string }> = {
  completed: { icon: '✅', color: '#22c55e' },
  'in-progress': { icon: '⏳', color: '#3b82f6' },
  pending: { icon: '⏸️', color: '#94a3b8' },
  failed: { icon: '❌', color: '#ef4444' },
};

/**
 * Task Metrics Component
 */
export const TaskMetrics: React.FC<TaskMetricsProps> = ({ data }) => {
  const total = data.reduce((sum, d) => sum + d.count, 0);

  // Format duration
  const formatDuration = (seconds: number) => {
    if (seconds === 0) return '-';
    if (seconds < 60) return `${seconds}s`;
    return `${Math.floor(seconds / 60)}m`;
  };

  return (
    <div className="apex-task-metrics">
      <div className="apex-task-metrics__header">
        <h4>📝 Task Status</h4>
      </div>

      {/* Pie chart visualization */}
      <div className="apex-task-metrics__chart">
        <svg viewBox="0 0 100 100" className="apex-task-metrics__pie">
          {(() => {
            let cumulative = 0;
            return data.map((item) => {
              const percentage = (item.count / total) * 100;
              const startAngle = (cumulative / 100) * 360;
              const endAngle = ((cumulative + percentage) / 100) * 360;
              cumulative += percentage;

              // Calculate arc path
              const startRad = ((startAngle - 90) * Math.PI) / 180;
              const endRad = ((endAngle - 90) * Math.PI) / 180;
              const largeArc = percentage > 50 ? 1 : 0;

              const x1 = 50 + 40 * Math.cos(startRad);
              const y1 = 50 + 40 * Math.sin(startRad);
              const x2 = 50 + 40 * Math.cos(endRad);
              const y2 = 50 + 40 * Math.sin(endRad);

              const d = `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`;

              return (
                <path
                  key={item.status}
                  d={d}
                  fill={statusConfig[item.status]?.color || '#64748b'}
                />
              );
            });
          })()}
          <circle cx="50" cy="50" r="25" fill="var(--bg-primary)" />
          <text
            x="50"
            y="50"
            textAnchor="middle"
            dominantBaseline="middle"
            className="apex-task-metrics__total"
          >
            {total}
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="apex-task-metrics__legend">
        {data.map((item) => (
          <div key={item.status} className="apex-task-metrics__legend-item">
            <span
              className="apex-task-metrics__legend-color"
              style={{ backgroundColor: statusConfig[item.status]?.color }}
            />
            <span className="apex-task-metrics__legend-icon">
              {statusConfig[item.status]?.icon}
            </span>
            <span className="apex-task-metrics__legend-label">
              {item.status}
            </span>
            <span className="apex-task-metrics__legend-count">{item.count}</span>
            <span className="apex-task-metrics__legend-percent">
              ({((item.count / total) * 100).toFixed(0)}%)
            </span>
            <span className="apex-task-metrics__legend-duration">
              {formatDuration(item.avgDuration)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
