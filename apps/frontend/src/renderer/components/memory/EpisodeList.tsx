/**
 * APEX Development Platform - Episode List
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { EpisodeCard } from './EpisodeCard';
import { LoadingSpinner } from '../common/LoadingSpinner';
import type { Episode } from '../../../preload/api/memory-api';

/** Episode list props */
export interface EpisodeListProps {
  episodes: Episode[];
  selectedEpisodeId: string | null;
  loading?: boolean;
  onSelect: (episode: Episode) => void;
}

/**
 * Episode List Component
 */
export const EpisodeList: React.FC<EpisodeListProps> = ({
  episodes,
  selectedEpisodeId,
  loading,
  onSelect,
}) => {
  if (loading) {
    return (
      <div className="apex-episode-list apex-episode-list--loading">
        <LoadingSpinner label="Loading episodes..." />
      </div>
    );
  }

  if (episodes.length === 0) {
    return (
      <div className="apex-episode-list apex-episode-list--empty">
        <p>🧠 No episodes found</p>
        <p>Memories will appear here as agents work on tasks</p>
      </div>
    );
  }

  return (
    <div className="apex-episode-list">
      {episodes.map((episode) => (
        <EpisodeCard
          key={episode.id}
          episode={episode}
          isSelected={episode.id === selectedEpisodeId}
          onClick={() => onSelect(episode)}
        />
      ))}
    </div>
  );
};
