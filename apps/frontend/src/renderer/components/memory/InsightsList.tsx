/**
 * APEX Development Platform - Insights List
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { MemoryInsight } from '../../../preload/api/memory-api';

/** Insights list props */
export interface InsightsListProps {
  insights: MemoryInsight[];
}

/** Insight type icons */
const typeIcons: Record<string, string> = {
  pattern: '🔄',
  trend: '📈',
  recommendation: '💡',
};

/** Insight type colors */
const typeColors: Record<string, string> = {
  pattern: '#8b5cf6',
  trend: '#3b82f6',
  recommendation: '#22c55e',
};

/**
 * Insights List Component
 */
export const InsightsList: React.FC<InsightsListProps> = ({ insights }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (insights.length === 0) {
    return (
      <div className="apex-insights-list apex-insights-list--empty">
        <p>💡 No insights yet</p>
        <p>Insights will be generated as patterns emerge from your episodes</p>
      </div>
    );
  }

  return (
    <div className="apex-insights-list">
      {insights.map((insight) => (
        <div key={insight.id} className="apex-insights-list__item">
          {/* Header */}
          <div className="apex-insights-list__header">
            <span
              className="apex-insights-list__type"
              style={{ backgroundColor: typeColors[insight.type] }}
            >
              {typeIcons[insight.type]} {insight.type}
            </span>
            <span
              className="apex-insights-list__confidence"
              title={`Confidence: ${(insight.confidence * 100).toFixed(0)}%`}
            >
              {insight.confidence >= 0.8
                ? '🟢'
                : insight.confidence >= 0.5
                ? '🟡'
                : '🔴'}
              {(insight.confidence * 100).toFixed(0)}%
            </span>
          </div>

          {/* Content */}
          <h4 className="apex-insights-list__title">{insight.title}</h4>
          <p className="apex-insights-list__description">{insight.description}</p>

          {/* Footer */}
          <div className="apex-insights-list__footer">
            <span className="apex-insights-list__episodes">
              📎 {insight.relatedEpisodes.length} related episodes
            </span>
            <span className="apex-insights-list__date">
              {formatDate(insight.createdAt)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
