/**
 * APEX Development Platform - Cost Tracker
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { AnalyticsData } from './AnalyticsView';

/** Cost tracker props */
export interface CostTrackerProps {
  data: AnalyticsData['costBreakdown'];
  total: number;
}

/** Provider icons */
const providerIcons: Record<string, string> = {
  openai: '🧠',
  anthropic: '🤖',
  copilot: '🐙',
  gemini: '✨',
  ollama: '🧬',
  lmstudio: '💻',
  openrouter: '🌐',
  azure: '☁️',
};

/**
 * Cost Tracker Component
 */
export const CostTracker: React.FC<CostTrackerProps> = ({ data, total }) => {
  // Sort by cost descending
  const sortedData = [...data].sort((a, b) => b.cost - a.cost);
  const maxCost = Math.max(...data.map((d) => d.cost), 0.01);

  return (
    <div className="apex-cost-tracker">
      <div className="apex-cost-tracker__header">
        <h4>💰 Cost Breakdown</h4>
        <span className="apex-cost-tracker__total">
          Total: ${total.toFixed(2)}
        </span>
      </div>

      <div className="apex-cost-tracker__list">
        {sortedData.map((item) => {
          const percentage = (item.cost / maxCost) * 100;
          
          return (
            <div key={item.provider} className="apex-cost-tracker__item">
              <div className="apex-cost-tracker__info">
                <span className="apex-cost-tracker__icon">
                  {providerIcons[item.provider] || '🌐'}
                </span>
                <span className="apex-cost-tracker__name">{item.provider}</span>
              </div>
              
              <div className="apex-cost-tracker__bar-container">
                <div
                  className="apex-cost-tracker__bar"
                  style={{ width: `${percentage}%` }}
                />
              </div>

              <div className="apex-cost-tracker__values">
                <span className="apex-cost-tracker__tokens">
                  {item.tokens >= 1000
                    ? `${(item.tokens / 1000).toFixed(0)}K`
                    : item.tokens}{' '}
                  tokens
                </span>
                <span
                  className={`apex-cost-tracker__cost ${
                    item.cost === 0 ? 'apex-cost-tracker__cost--free' : ''
                  }`}
                >
                  {item.cost === 0 ? 'Free' : `$${item.cost.toFixed(2)}`}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="apex-cost-tracker__footer">
        <span>
          Total Tokens:{' '}
          {data.reduce((sum, d) => sum + d.tokens, 0).toLocaleString()}
        </span>
        <span className="apex-cost-tracker__savings">
          🌟 Saved:{' '}
          ${data.filter((d) => d.cost === 0).reduce((sum, d) => sum + d.tokens * 0.00003, 0).toFixed(2)}
          {' '}(local models)
        </span>
      </div>
    </div>
  );
};
