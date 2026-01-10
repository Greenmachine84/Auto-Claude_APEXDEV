/**
 * APEX Development Platform - Memory Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Episode,
  MemorySearchOptions,
  MemorySearchResult,
  MemoryInsight,
  MemoryStats,
} from '../../preload/api/memory-api';

/** Memory state */
export interface MemoryState {
  episodes: Episode[];
  insights: MemoryInsight[];
  stats: MemoryStats | null;
  selectedEpisodeId: string | null;
  searchResults: MemorySearchResult[] | null;
  loading: boolean;
  error: Error | null;
}

/** Memory actions */
export interface MemoryActions {
  // Operations
  loadMemory: () => Promise<void>;
  search: (options: MemorySearchOptions) => Promise<MemorySearchResult[]>;
  clearSearch: () => void;
  addEpisode: (content: string, metadata: Episode['metadata']) => Promise<Episode>;
  deleteEpisode: (id: string) => Promise<void>;

  // Selection
  selectEpisode: (id: string | null) => void;
  getSelectedEpisode: () => Episode | undefined;

  // Events
  handleEpisodeAdded: (episode: Episode) => void;
  handleEpisodeDeleted: (episodeId: string) => void;
}

/**
 * Memory Store - Episodic memory state
 */
export const useMemoryStore = create<MemoryState & MemoryActions>()(
  devtools(
    (set, get) => ({
      // Initial state
      episodes: [],
      insights: [],
      stats: null,
      selectedEpisodeId: null,
      searchResults: null,
      loading: false,
      error: null,

      // Load memory
      loadMemory: async () => {
        set({ loading: true, error: null });
        try {
          const [episodes, insights, stats] = await Promise.all([
            window.apex.memory.list({ limit: 100 }),
            window.apex.memory.getInsights(),
            window.apex.memory.getStats(),
          ]);
          set({ episodes: episodes as Episode[], insights: insights as MemoryInsight[], stats: stats as MemoryStats | null, loading: false });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error : new Error('Failed to load memory'),
          });
        }
      },

      // Search
      search: async (options) => {
        const results = await window.apex.memory.search(options as Record<string, unknown>) as MemorySearchResult[];
        set({ searchResults: results });
        return results;
      },

      // Clear search
      clearSearch: () => set({ searchResults: null }),

      // Add episode
      addEpisode: async (content, metadata) => {
        const episode = await window.apex.memory.add(content, metadata);
        set((state) => ({ episodes: [episode as Episode, ...state.episodes] }));
        return episode;
      },

      // Delete episode
      deleteEpisode: async (id) => {
        await window.apex.memory.delete(id);
        set((state) => ({
          episodes: state.episodes.filter((e) => e.id !== id),
          selectedEpisodeId: state.selectedEpisodeId === id ? null : state.selectedEpisodeId,
        }));
      },

      // Select episode
      selectEpisode: (id) => set({ selectedEpisodeId: id }),

      // Get selected episode
      getSelectedEpisode: () => {
        const { episodes, selectedEpisodeId } = get();
        return episodes.find((e) => e.id === selectedEpisodeId);
      },

      // Handle episode added event
      handleEpisodeAdded: (episode) => {
        set((state) => {
          if (state.episodes.find((e) => e.id === episode.id)) return state;
          return { episodes: [episode, ...state.episodes] };
        });
      },

      // Handle episode deleted event
      handleEpisodeDeleted: (episodeId) => {
        set((state) => ({
          episodes: state.episodes.filter((e) => e.id !== episodeId),
          selectedEpisodeId:
            state.selectedEpisodeId === episodeId ? null : state.selectedEpisodeId,
        }));
      },
    }),
    { name: 'MemoryStore' }
  )
);

