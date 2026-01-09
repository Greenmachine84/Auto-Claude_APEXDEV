/**
 * APEX Development Platform - Memory API Types
 * Phase 2: Memory & LLM Architecture
 * 
 * Stub implementation for frontend compatibility
 */

/** Episode type */
// Episode metadata type for consumers
export type EpisodeMetadata = Episode['metadata'];

export interface Episode {
  id: string;
  content: string;
  embedding?: number[];
  metadata: {
    timestamp: string;
    source: string;
    projectId?: string;
    taskId?: string;
    tags?: string[];
  };
  createdAt: string;
  updatedAt: string;
}

/** Memory search options */
export interface MemorySearchOptions {
  query?: string;
  projectId?: string;
  tags?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  limit?: number;
  offset?: number;
}

/** Memory search result */
export interface MemorySearchResult {
  episode: Episode;
  score: number;
}

/** Memory insight */
export interface MemoryInsight {
  id: string;
  type: 'pattern' | 'trend' | 'summary';
  title: string;
  description: string;
  confidence: number;
  relatedEpisodes: string[];
  createdAt: string;
}

/** Memory stats */
export interface MemoryStats {
  totalEpisodes: number;
  storageUsed: number;
  lastUpdated: string;
  topTags: { tag: string; count: number }[];
}

/** Memory API interface */
export interface MemoryAPI {
  list: (options?: Partial<MemorySearchOptions>) => Promise<Episode[]>;
  search: (options: MemorySearchOptions) => Promise<MemorySearchResult[]>;
  add: (content: string, metadata: Episode['metadata']) => Promise<Episode>;
  delete: (id: string) => Promise<void>;
  getInsights: () => Promise<MemoryInsight[]>;
  getStats: () => Promise<MemoryStats>;
  onEpisodeAdded: (callback: (episode: Episode) => void) => () => void;
  onEpisodeDeleted: (callback: (episodeId: string) => void) => () => void;
}

/** Create stub memory API */
export const createMemoryAPI = (): MemoryAPI => ({
  list: async () => [],
  search: async () => [],
  add: async (content, metadata) => ({
    id: crypto.randomUUID(),
    content,
    metadata,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }),
  delete: async () => {},
  getInsights: async () => [],
  getStats: async () => ({
    totalEpisodes: 0,
    storageUsed: 0,
    lastUpdated: new Date().toISOString(),
    topTags: [],
  }),
  onEpisodeAdded: () => () => {},
  onEpisodeDeleted: () => () => {},
});
