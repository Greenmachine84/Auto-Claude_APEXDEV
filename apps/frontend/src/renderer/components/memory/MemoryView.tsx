/**
 * APEX Development Platform - Memory View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { EpisodeList } from './EpisodeList';
import { EpisodeDetail } from './EpisodeDetail';
import { MemorySearch } from './MemorySearch';
import { InsightsList } from './InsightsList';
import { Button } from '../common/Button';
import { useMemory } from '../../hooks/useMemory';
import type { Episode, MemorySearchOptions, MemoryInsight } from '../../../preload/api/memory-api';

/**
 * Memory View Component
 */
const MemoryView: React.FC = () => {
  const {
    episodes,
    insights,
    stats,
    loading,
    error,
    search,
    refresh,
  } = useMemory();

  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);
  const [searchResults, setSearchResults] = useState<Episode[] | null>(null);
  const [activeTab, setActiveTab] = useState<'episodes' | 'insights'>('episodes');

  // Handle search
  const handleSearch = useCallback(
    async (options: MemorySearchOptions) => {
      const results = await search(options);
      setSearchResults(results.map((r) => r.episode));
    },
    [search]
  );

  // Clear search
  const handleClearSearch = useCallback(() => {
    setSearchResults(null);
  }, []);

  // Handle episode selection
  const handleSelectEpisode = useCallback((episode: Episode) => {
    setSelectedEpisode(episode);
  }, []);

  // Subscribe to new episodes
  useEffect(() => {
    const unsubscribe = window.apex.memory.onEpisodeAdded(() => {
      refresh();
    });
    return unsubscribe;
  }, [refresh]);

  const displayedEpisodes = searchResults || episodes;

  if (error) {
    return (
      <div className="apex-memory-view apex-memory-view--error">
        <p>Error loading memory: {error.message}</p>
        <Button onClick={refresh}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="apex-memory-view">
      {/* Header */}
      <div className="apex-memory-view__header">
        <div className="apex-memory-view__tabs">
          <button
            className={`apex-memory-view__tab ${
              activeTab === 'episodes' ? 'apex-memory-view__tab--active' : ''
            }`}
            onClick={() => setActiveTab('episodes')}
          >
            Episodes ({displayedEpisodes.length})
          </button>
          <button
            className={`apex-memory-view__tab ${
              activeTab === 'insights' ? 'apex-memory-view__tab--active' : ''
            }`}
            onClick={() => setActiveTab('insights')}
          >
            Insights ({insights.length})
          </button>
        </div>

        {stats && (
          <div className="apex-memory-view__stats">
            <span>Total: {stats.totalEpisodes}</span>
            <span>Storage: {(stats.storageUsed / 1024 / 1024).toFixed(2)} MB</span>
          </div>
        )}
      </div>

      {/* Search */}
      {activeTab === 'episodes' && (
        <MemorySearch
          onSearch={handleSearch}
          onClear={handleClearSearch}
          isSearchActive={searchResults !== null}
        />
      )}

      {/* Content */}
      <div className="apex-memory-view__content">
        {activeTab === 'episodes' ? (
          <>
            <div className="apex-memory-view__list">
              <EpisodeList
                episodes={displayedEpisodes}
                selectedEpisodeId={selectedEpisode?.id || null}
                loading={loading}
                onSelect={handleSelectEpisode}
              />
            </div>

            {selectedEpisode && (
              <div className="apex-memory-view__detail">
                <EpisodeDetail
                  episode={selectedEpisode}
                  onClose={() => setSelectedEpisode(null)}
                />
              </div>
            )}
          </>
        ) : (
          <InsightsList insights={insights} />
        )}
      </div>
    </div>
  );
};

export default MemoryView;
