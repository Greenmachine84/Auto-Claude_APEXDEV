/**
 * APEX Development Platform - Episode Card
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { Episode } from '../../../preload/api/memory-api';

/** Type icons */
const typeIcons: Record<string, string> = {
  task: '📝',
  conversation: '💬',
  code: '💻',
  decision: '⚖️',
  insight: '💡',
};

/** Type colors */
const typeColors: Record<string, string> = {
  task: '#3b82f6',
  conversation: '#8b5cf6',
  code: '#22c55e',
  decision: '#f59e0b',
  insight: '#ec4899',
};

/** Episode card props */
export interface EpisodeCardProps {
  episode: Episode;
  isSelected?: boolean;
  onClick: () => void;
}

/**
 * Episode Card Component
 */
export const EpisodeCard: React.FC<EpisodeCardProps> = ({
  episode,
  isSelected,
  onClick,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncateContent = (content: string, maxLength = 150) => {
    if (content.length <= maxLength) return content;
    return content.slice(0, maxLength).trim() + '...';
  };

  return (
    <div
      className={`apex-episode-card ${isSelected ? 'apex-episode-card--selected' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {/* Header */}
      <div className="apex-episode-card__header">
        <span
          className="apex-episode-card__type"
          style={{ backgroundColor: (typeColors[episode.metadata?.type ?? 'task'] ?? '#6b7280') }}
        >
          {(typeIcons[episode.metadata?.type ?? 'task'] ?? '📝')} {episode.metadata?.type ?? "task"}
        </span>
        {episode.metadata?.importance && (
          <span
            className="apex-episode-card__importance"
            title={`Importance: ${episode.metadata.importance}/10`}
          >
            {'★'.repeat(Math.ceil(((episode.metadata?.importance === "high" ? 10 : episode.metadata?.importance === "medium" ? 5 : 2) / 2)))}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="apex-episode-card__content">
        {truncateContent(episode.content)}
      </div>

      {/* Tags */}
      {episode.metadata.tags && episode.metadata.tags.length > 0 && (
        <div className="apex-episode-card__tags">
          {episode.metadata.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="apex-episode-card__tag">
              {tag}
            </span>
          ))}
          {episode.metadata.tags.length > 3 && (
            <span className="apex-episode-card__tag apex-episode-card__tag--more">
              +{episode.metadata.tags.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="apex-episode-card__footer">
        <span className="apex-episode-card__date">
          {formatDate(episode.createdAt)}
        </span>
        {episode.metadata.source && (
          <span className="apex-episode-card__source">
            {episode.metadata.source}
          </span>
        )}
      </div>
    </div>
  );
};


