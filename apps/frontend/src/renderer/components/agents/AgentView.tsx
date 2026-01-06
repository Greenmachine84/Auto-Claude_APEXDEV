/**
 * APEX Development Platform - Agent View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { AgentList } from './AgentList';
import { AgentDetail } from './AgentDetail';
import { AgentPoolStatus } from './AgentPoolStatus';
import { Button } from '../common/Button';
import { useAgents } from '../../hooks/useAgents';
import type { Agent, AgentType } from '../../../preload/api/agent-api';

/**
 * Agent View Component
 */
const AgentView: React.FC = () => {
  const {
    agents,
    poolStatus,
    loading,
    error,
    startAgent,
    stopAgent,
    refresh,
  } = useAgents();

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showPoolStatus, setShowPoolStatus] = useState(false);

  // Handle agent selection
  const handleSelectAgent = useCallback((agent: Agent) => {
    setSelectedAgent(agent);
  }, []);

  // Handle start agent
  const handleStartAgent = useCallback(
    async (type: AgentType) => {
      await startAgent(type);
    },
    [startAgent]
  );

  // Handle stop agent
  const handleStopAgent = useCallback(
    async (agentId: string) => {
      await stopAgent(agentId);
      if (selectedAgent?.id === agentId) {
        setSelectedAgent(null);
      }
    },
    [stopAgent, selectedAgent]
  );

  // Subscribe to agent updates
  useEffect(() => {
    const unsubscribers = [
      window.apex.agents.onAgentUpdate((agent) => {
        if (selectedAgent?.id === agent.id) {
          setSelectedAgent(agent);
        }
        refresh();
      }),
      window.apex.agents.onPoolUpdate(() => {
        refresh();
      }),
    ];

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [refresh, selectedAgent]);

  if (error) {
    return (
      <div className="apex-agent-view apex-agent-view--error">
        <p>Error loading agents: {error.message}</p>
        <Button onClick={refresh}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="apex-agent-view">
      {/* Header */}
      <div className="apex-agent-view__header">
        <h2>AI Agents</h2>
        <div className="apex-agent-view__actions">
          <Button
            variant="ghost"
            onClick={() => setShowPoolStatus(!showPoolStatus)}
          >
            {showPoolStatus ? 'Hide' : 'Show'} Pool Status
          </Button>
          <Button variant="primary" onClick={() => handleStartAgent('coder')}>
            + Start Coder
          </Button>
        </div>
      </div>

      {/* Pool Status */}
      {showPoolStatus && poolStatus && (
        <AgentPoolStatus status={poolStatus} />
      )}

      {/* Content */}
      <div className="apex-agent-view__content">
        {/* Agent List */}
        <div className="apex-agent-view__list">
          <AgentList
            agents={agents}
            selectedAgentId={selectedAgent?.id || null}
            loading={loading}
            onSelect={handleSelectAgent}
            onStart={handleStartAgent}
            onStop={handleStopAgent}
          />
        </div>

        {/* Agent Detail */}
        {selectedAgent && (
          <div className="apex-agent-view__detail">
            <AgentDetail
              agent={selectedAgent}
              onStop={() => handleStopAgent(selectedAgent.id)}
              onClose={() => setSelectedAgent(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentView;
