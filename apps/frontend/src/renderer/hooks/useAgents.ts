/**
 * APEX Development Platform - useAgents Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useState, useEffect, useCallback } from 'react';
import type { Agent, AgentType, CreateAgentInput, AgentPoolStatus } from '../../preload/api/agent-api';

/** Agents hook return type */
export interface UseAgentsReturn {
  agents: Agent[];
  poolStatus: AgentPoolStatus | null;
  loading: boolean;
  error: Error | null;
  // Operations
  startAgent: (input: CreateAgentInput) => Promise<Agent>;
  stopAgent: (id: string) => Promise<void>;
  pauseAgent: (id: string) => Promise<void>;
  resumeAgent: (id: string) => Promise<void>;
  // Queries
  getById: (id: string) => Agent | undefined;
  getByType: (type: AgentType) => Agent[];
  getActive: () => Agent[];
  // Actions
  refresh: () => Promise<void>;
}

/**
 * Agents Hook - Manage agent state and operations
 */
export function useAgents(): UseAgentsReturn {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [poolStatus, setPoolStatus] = useState<AgentPoolStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Load agents
  const loadAgents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [agentList, status] = await Promise.all([
        window.apex.agents.list(),
        window.apex.agents.getPoolStatus(),
      ]);
      setAgents(agentList as Agent[]);
      setPoolStatus(status as AgentPoolStatus | null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load agents'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  // Subscribe to agent events
  useEffect(() => {
    const unsubscribeStarted = window.apex.agents.onStarted((agent) => {
      setAgents((prev) => [...prev, agent as Agent]);
    });

    const unsubscribeStopped = window.apex.agents.onStopped((agentId) => {
      setAgents((prev) => prev.filter((a) => a.id !== agentId) as Agent[]);
    });

    const unsubscribeStatusChanged = window.apex.agents.onStatusChanged(({ agentId, status }) => {
      setAgents((prev) =>
        prev.map((a) => (a.id === agentId ? { ...a, status: status as import('../../preload/api/agent-api').AgentStatus } : a))
      );
    });

    const unsubscribePoolUpdated = window.apex.agents.onPoolUpdated((status) => {
      setPoolStatus(status as AgentPoolStatus | null);
    });

    return () => {
      unsubscribeStarted();
      unsubscribeStopped();
      unsubscribeStatusChanged();
      unsubscribePoolUpdated();
    };
  }, []);

  // Start agent
  const startAgent = useCallback(async (input: CreateAgentInput): Promise<Agent> => {
    const agent = await window.apex.agents.start(input) as Agent;
    return agent;
  }, []);

  // Stop agent
  const stopAgent = useCallback(async (id: string): Promise<void> => {
    await window.apex.agents.stop(id);
  }, []);

  // Pause agent
  const pauseAgent = useCallback(async (id: string): Promise<void> => {
    await window.apex.agents.pause(id);
  }, []);

  // Resume agent
  const resumeAgent = useCallback(async (id: string): Promise<void> => {
    await window.apex.agents.resume(id);
  }, []);

  // Get by ID
  const getById = useCallback(
    (id: string): Agent | undefined => {
      return agents.find((a) => a.id === id);
    },
    [agents]
  );

  // Get by type
  const getByType = useCallback(
    (type: AgentType): Agent[] => {
      return agents.filter((a) => a.type === type);
    },
    [agents]
  );

  // Get active agents
  const getActive = useCallback((): Agent[] => {
    return agents.filter((a) => a.status === 'running');
  }, [agents]);

  return {
    agents,
    poolStatus,
    loading,
    error,
    startAgent,
    stopAgent,
    pauseAgent,
    resumeAgent,
    getById,
    getByType,
    getActive,
    refresh: loadAgents,
  };
}


