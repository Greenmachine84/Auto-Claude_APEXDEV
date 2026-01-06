/**
 * APEX Development Platform - Memory IPC Handlers
 * Phase 4: UI, Integrations & Analytics
 *
 * Handles memory-related IPC communication between renderer and main process.
 */

import { IpcMain } from 'electron';
import { IPCChannels } from './index';
import { createIPCSuccess, createIPCError, IPCResponse } from './ipc-handler';
import { BackendService } from '../services/backend-service';

/** Memory tier levels */
export type MemoryTier = 'L1' | 'L2' | 'L3';

/** Episode status */
export type EpisodeStatus = 'active' | 'archived' | 'deleted';

/** Episode definition */
export interface Episode {
  id: string;
  taskId: string;
  agentId: string;
  tier: MemoryTier;
  status: EpisodeStatus;
  input: string;
  output: string;
  context?: Record<string, unknown>;
  tokens: number;
  createdAt: string;
  accessedAt: string;
  accessCount: number;
  embedding?: number[];
  metadata?: Record<string, unknown>;
}

/** Search result with relevance score */
export interface SearchResult {
  episode: Episode;
  score: number;
  highlights?: string[];
}

/** Memory insights */
export interface MemoryInsights {
  totalEpisodes: number;
  episodesByTier: Record<MemoryTier, number>;
  recentPatterns: string[];
  topAgents: { agentId: string; episodeCount: number }[];
  storageUsed: number;
  lastUpdated: string;
}

/** Search params */
export interface MemorySearchParams {
  query: string;
  tier?: MemoryTier;
  agentId?: string;
  taskId?: string;
  limit?: number;
  semantic?: boolean;
}

/** Get episodes params */
export interface GetEpisodesParams {
  tier?: MemoryTier;
  agentId?: string;
  taskId?: string;
  status?: EpisodeStatus;
  limit?: number;
  offset?: number;
  sortBy?: 'createdAt' | 'accessedAt' | 'accessCount';
  sortOrder?: 'asc' | 'desc';
}

/** Store episode params */
export interface StoreEpisodeParams {
  taskId: string;
  agentId: string;
  input: string;
  output: string;
  context?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Register memory IPC handlers
 */
export function registerMemoryIPCHandlers(ipcMain: IpcMain): void {
  const backend = BackendService.getInstance();

  // Search memory
  ipcMain.handle(
    IPCChannels.MEMORY_SEARCH,
    async (_, params: MemorySearchParams): Promise<IPCResponse<SearchResult[]>> => {
      try {
        const results = await backend.request<SearchResult[]>('memory.search', params);
        return createIPCSuccess(results);
      } catch (error) {
        return createIPCError('MEMORY_SEARCH_FAILED', (error as Error).message);
      }
    }
  );

  // Get single episode
  ipcMain.handle(
    IPCChannels.MEMORY_GET,
    async (_, id: string): Promise<IPCResponse<Episode>> => {
      try {
        const episode = await backend.request<Episode>('memory.get', { id });
        return createIPCSuccess(episode);
      } catch (error) {
        return createIPCError('MEMORY_GET_FAILED', (error as Error).message);
      }
    }
  );

  // Store new episode
  ipcMain.handle(
    IPCChannels.MEMORY_STORE,
    async (_, params: StoreEpisodeParams): Promise<IPCResponse<Episode>> => {
      try {
        const episode = await backend.request<Episode>('memory.store', params);
        return createIPCSuccess(episode);
      } catch (error) {
        return createIPCError('MEMORY_STORE_FAILED', (error as Error).message);
      }
    }
  );

  // Delete episode
  ipcMain.handle(
    IPCChannels.MEMORY_DELETE,
    async (_, id: string): Promise<IPCResponse<boolean>> => {
      try {
        await backend.request('memory.delete', { id });
        return createIPCSuccess(true);
      } catch (error) {
        return createIPCError('MEMORY_DELETE_FAILED', (error as Error).message);
      }
    }
  );

  // Get episodes with filtering
  ipcMain.handle(
    IPCChannels.MEMORY_EPISODES,
    async (_, params: GetEpisodesParams = {}): Promise<IPCResponse<Episode[]>> => {
      try {
        const episodes = await backend.request<Episode[]>('memory.episodes', params);
        return createIPCSuccess(episodes);
      } catch (error) {
        return createIPCError('MEMORY_EPISODES_FAILED', (error as Error).message);
      }
    }
  );

  // Get memory insights
  ipcMain.handle(
    IPCChannels.MEMORY_INSIGHTS,
    async (): Promise<IPCResponse<MemoryInsights>> => {
      try {
        const insights = await backend.request<MemoryInsights>('memory.insights', {});
        return createIPCSuccess(insights);
      } catch (error) {
        return createIPCError('MEMORY_INSIGHTS_FAILED', (error as Error).message);
      }
    }
  );

  console.log('[IPC] Memory handlers registered');
}
