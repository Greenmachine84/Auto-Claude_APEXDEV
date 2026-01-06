/**
 * APEX Development Platform - Agent Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Agent,
  AgentType,
  AgentStatus,
  CreateAgentInput,
  AgentPoolStatus,
} from '../../preload/api/agent-api';

/** Agent state */
export interface AgentState {
  agents: Agent[];
  selectedAgentId: string | null;
  poolStatus: AgentPoolStatus | null;
  loading: boolean;
  error: Error | null;
}

/** Agent actions */
export interface AgentActions {
  // Operations
  loadAgents: () => Promise<void>;
  startAgent: (input: CreateAgentInput) => Promise<Agent>;
  stopAgent: (id: string) => Promise<void>;
  pauseAgent: (id: string) => Promise<void>;
  resumeAgent: (id: string) => Promise<void>;

  // Selection
  selectAgent: (id: string | null) => void;
  getSelectedAgent: () => Agent | undefined;

  // Queries
  getAgentsByType: (type: AgentType) => Agent[];
  getAgentsByStatus: (status: AgentStatus) => Agent[];
  getActiveCount: () => number;

  // Events
  handleAgentStarted: (agent: Agent) => void;
  handleAgentStopped: (agentId: string) => void;
  handleAgentStatusChanged: (agentId: string, status: AgentStatus) => void;
  handlePoolUpdated: (status: AgentPoolStatus) => void;
}

/**
 * Agent Store - Agent management state
 */
export const useAgentStore = create<AgentState & AgentActions>()(
  devtools(
    (set, get) => ({
      // Initial state
      agents: [],
      selectedAgentId: null,
      poolStatus: null,
      loading: false,
      error: null,

      // Load agents
      loadAgents: async () => {
        set({ loading: true, error: null });
        try {
          const [agents, poolStatus] = await Promise.all([
            window.apex.agents.list(),
            window.apex.agents.getPoolStatus(),
          ]);
          set({ agents, poolStatus, loading: false });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error : new Error('Failed to load agents'),
          });
        }
      },

      // Start agent
      startAgent: async (input) => {
        const agent = await window.apex.agents.start(input);
        set((state) => ({ agents: [...state.agents, agent] }));
        return agent;
      },

      // Stop agent
      stopAgent: async (id) => {
        await window.apex.agents.stop(id);
        set((state) => ({
          agents: state.agents.filter((a) => a.id !== id),
          selectedAgentId: state.selectedAgentId === id ? null : state.selectedAgentId,
        }));
      },

      // Pause agent
      pauseAgent: async (id) => {
        await window.apex.agents.pause(id);
        set((state) => ({
          agents: state.agents.map((a) =>
            a.id === id ? { ...a, status: 'paused' as AgentStatus } : a
          ),
        }));
      },

      // Resume agent
      resumeAgent: async (id) => {
        await window.apex.agents.resume(id);
        set((state) => ({
          agents: state.agents.map((a) =>
            a.id === id ? { ...a, status: 'running' as AgentStatus } : a
          ),
        }));
      },

      // Select agent
      selectAgent: (id) => set({ selectedAgentId: id }),

      // Get selected agent
      getSelectedAgent: () => {
        const { agents, selectedAgentId } = get();
        return agents.find((a) => a.id === selectedAgentId);
      },

      // Get agents by type
      getAgentsByType: (type) => get().agents.filter((a) => a.type === type),

      // Get agents by status
      getAgentsByStatus: (status) => get().agents.filter((a) => a.status === status),

      // Get active count
      getActiveCount: () => get().agents.filter((a) => a.status === 'running').length,

      // Handle agent started event
      handleAgentStarted: (agent) => {
        set((state) => {
          if (state.agents.find((a) => a.id === agent.id)) return state;
          return { agents: [...state.agents, agent] };
        });
      },

      // Handle agent stopped event
      handleAgentStopped: (agentId) => {
        set((state) => ({
          agents: state.agents.filter((a) => a.id !== agentId),
          selectedAgentId: state.selectedAgentId === agentId ? null : state.selectedAgentId,
        }));
      },

      // Handle agent status changed event
      handleAgentStatusChanged: (agentId, status) => {
        set((state) => ({
          agents: state.agents.map((a) => (a.id === agentId ? { ...a, status } : a)),
        }));
      },

      // Handle pool updated event
      handlePoolUpdated: (status) => set({ poolStatus: status }),
    }),
    { name: 'AgentStore' }
  )
);
