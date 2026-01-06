/**
 * APEX Development Platform - Memory API (Preload)
 * Phase 4: UI, Integrations & Analytics
 *
 * Episodic memory API exposed to renderer.
 */

import { ipcRenderer } from 'electron';

/** Memory episode */
export interface Episode {
  id: string;
  content: string;
  embedding?: number[];
  metadata: EpisodeMetadata;
  createdAt: string;
  updatedAt: string;
}

/** Episode metadata */
export interface EpisodeMetadata {
  type: 'task' | 'conversation' | 'code' | 'decision' | 'insight';
  source?: string;
  taskId?: string;
  agentId?: string;
  importance?: number;
  tags?: string[];
}

/** Memory search options */
export interface MemorySearchOptions {
  query: string;
  limit?: number;
  threshold?: number;
  types?: EpisodeMetadata['type'][];
  tags?: string[];
  dateRange?: {
    start?: string;
    end?: string;
  };
}

/** Memory search result */
export interface MemorySearchResult {
  episode: Episode;
  score: number;
  highlights?: string[];
}

/** Memory insight */
export interface MemoryInsight {
  id: string;
  type: 'pattern' | 'trend' | 'recommendation';
  title: string;
  description: string;
  relatedEpisodes: string[];
  confidence: number;
  createdAt: string;
}

/** Memory statistics */
export interface MemoryStats {
  totalEpisodes: number;
  episodesByType: Record<string, number>;
  storageUsed: number;
  lastUpdated: string;
}

/**
 * Memory API
 */
export const memoryAPI = {
  /**
   * Search memory with semantic query
   */
  search: (options: MemorySearchOptions): Promise<MemorySearchResult[]> =>
    ipcRenderer.invoke('memory:search', options),

  /**
   * Get episode by ID
   */
  get: (id: string): Promise<Episode | null> =>
    ipcRenderer.invoke('memory:get', id),

  /**
   * Store new episode
   */
  store: (content: string, metadata: EpisodeMetadata): Promise<Episode> =>
    ipcRenderer.invoke('memory:store', content, metadata),

  /**
   * Update episode
   */
  update: (id: string, content: string, metadata?: Partial<EpisodeMetadata>): Promise<Episode> =>
    ipcRenderer.invoke('memory:update', id, content, metadata),

  /**
   * Delete episode
   */
  delete: (id: string): Promise<boolean> =>
    ipcRenderer.invoke('memory:delete', id),

  /**
   * Get recent episodes
   */
  recent: (limit?: number): Promise<Episode[]> =>
    ipcRenderer.invoke('memory:recent', limit),

  /**
   * Get episodes by task
   */
  byTask: (taskId: string): Promise<Episode[]> =>
    ipcRenderer.invoke('memory:byTask', taskId),

  /**
   * Get episodes by tag
   */
  byTag: (tag: string): Promise<Episode[]> =>
    ipcRenderer.invoke('memory:byTag', tag),

  /**
   * Get memory insights
   */
  insights: (): Promise<MemoryInsight[]> =>
    ipcRenderer.invoke('memory:insights'),

  /**
   * Generate insight from episodes
   */
  generateInsight: (episodeIds: string[]): Promise<MemoryInsight> =>
    ipcRenderer.invoke('memory:generateInsight', episodeIds),

  /**
   * Get memory statistics
   */
  stats: (): Promise<MemoryStats> =>
    ipcRenderer.invoke('memory:stats'),

  /**
   * Export memory to file
   */
  export: (path: string): Promise<boolean> =>
    ipcRenderer.invoke('memory:export', path),

  /**
   * Import memory from file
   */
  import: (path: string): Promise<number> =>
    ipcRenderer.invoke('memory:import', path),

  /**
   * Clear all memory
   */
  clear: (): Promise<boolean> =>
    ipcRenderer.invoke('memory:clear'),

  /**
   * Subscribe to new episodes
   */
  onEpisodeAdded: (callback: (episode: Episode) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, episode: Episode) => callback(episode);
    ipcRenderer.on('memory:episodeAdded', listener);
    return () => ipcRenderer.removeListener('memory:episodeAdded', listener);
  },

  /**
   * Subscribe to insight generation
   */
  onInsightGenerated: (callback: (insight: MemoryInsight) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, insight: MemoryInsight) =>
      callback(insight);
    ipcRenderer.on('memory:insightGenerated', listener);
    return () => ipcRenderer.removeListener('memory:insightGenerated', listener);
  },
};
