/**
 * APEX Development Platform - useMemory Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useState, useEffect, useCallback } from 'react';
import type {
  Episode,
  MemorySearchOptions,
  MemorySearchResult,
  MemoryInsight,
  MemoryStats,
} from '../../preload/api/memory-api';

/** Memory hook return type */
export interface UseMemoryReturn {
  episodes: Episode[];
  insights: MemoryInsight[];
  stats: MemoryStats | null;
  loading: boolean;
  error: Error | null;
  // Operations
  search: (options: MemorySearchOptions) => Promise<MemorySearchResult[]>;
  addEpisode: (content: string, metadata: Episode['metadata']) => Promise<Episode>;
  deleteEpisode: (id: string) => Promise<void>;
  // Actions
  refresh: () => Promise<void>;
}

/**
 * Memory Hook - Manage episodic memory state and operations
 */
export function useMemory(): UseMemoryReturn {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [insights, setInsights] = useState<MemoryInsight[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Load memory data
  const loadMemory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [episodeList, insightList, memoryStats] = await Promise.all([
        window.apex.memory.list({ limit: 100 }),
        window.apex.memory.getInsights(),
        window.apex.memory.getStats(),
      ]);
      setEpisodes(episodeList as Episode[]);
      setInsights(insightList as MemoryInsight[]);
      setStats(memoryStats as MemoryStats);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load memory'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadMemory();
  }, [loadMemory]);

  // Subscribe to episode events
  useEffect(() => {
    const unsubscribeAdded = window.apex.memory.onEpisodeAdded((episode) => {
      setEpisodes((prev) => [episode as Episode, ...prev]);
    });

    const unsubscribeDeleted = window.apex.memory.onEpisodeDeleted((episodeId) => {
      setEpisodes((prev) => prev.filter((e) => e.id !== episodeId));
    });

    return () => {
      unsubscribeAdded();
      unsubscribeDeleted();
    };
  }, []);

  // Search episodes
  const search = useCallback(
    async (options: MemorySearchOptions): Promise<MemorySearchResult[]> => {
      return window.apex.memory.search(options as Record<string, unknown>) as Promise<MemorySearchResult[]>;
    },
    []
  );

  // Add episode
  const addEpisode = useCallback(
    async (content: string, metadata: Episode['metadata']): Promise<Episode> => {
      return window.apex.memory.add(content, metadata) as Promise<Episode>;
    },
    []
  );

  // Delete episode
  const deleteEpisode = useCallback(async (id: string): Promise<void> => {
    await window.apex.memory.delete(id);
  }, []);

  return {
    episodes,
    insights,
    stats,
    loading,
    error,
    search,
    addEpisode,
    deleteEpisode,
    refresh: loadMemory,
  };
}

