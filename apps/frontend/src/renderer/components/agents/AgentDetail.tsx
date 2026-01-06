/**
 * APEX Development Platform - Agent Detail
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect } from 'react';
import { Button } from '../common/Button';
import { AgentLogs } from './AgentLogs';
import type { Agent } from '../../../preload/api/agent-api';

/** Agent detail props */
export interface AgentDetailProps {
  agent: Agent;
  onStop: () => void;
  onClose: () => void;
}

/**
 * Agent Detail Component
 */
export const AgentDetail: React.FC<AgentDetailProps> = ({
  agent,
  onStop,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'info' | 'logs' | 'metrics'>('info');
  const [logs, setLogs] = useState<string[]>([]);

  // Fetch logs
  useEffect(() => {
    const fetchLogs = async () => {
      const agentLogs = await window.apex.agents.logs(agent.id, 100);
      setLogs(agentLogs);
    };
    fetchLogs();

    // Subscribe to new logs
    const unsubscribe = window.apex.agents.onAgentLog((agentId, log) => {
      if (agentId === agent.id) {
        setLogs((prev) => [...prev.slice(-99), log]);
      }
    });

    return unsubscribe;
  }, [agent.id]);

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="apex-agent-detail">
      {/* Header */}
      <div className="apex-agent-detail__header">
        <h3>
          {agent.type.charAt(0).toUpperCase() + agent.type.slice(1)} Agent
        </h3>
        <button
          className="apex-agent-detail__close"
          onClick={onClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      {/* Tabs */}
      <div className="apex-agent-detail__tabs">
        {(['info', 'logs', 'metrics'] as const).map((tab) => (
          <button
            key={tab}
            className={`apex-agent-detail__tab ${
              activeTab === tab ? 'apex-agent-detail__tab--active' : ''
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="apex-agent-detail__content">
        {activeTab === 'info' && (
          <div className="apex-agent-detail__info">
            <dl>
              <dt>ID</dt>
              <dd>{agent.id}</dd>
              <dt>Type</dt>
              <dd>{agent.type}</dd>
              <dt>Status</dt>
              <dd>{agent.status}</dd>
              <dt>Started</dt>
              <dd>{formatDate(agent.startedAt)}</dd>
              <dt>Last Active</dt>
              <dd>{formatDate(agent.lastActiveAt)}</dd>
              {agent.taskId && (
                <>
                  <dt>Current Task</dt>
                  <dd>{agent.taskId}</dd>
                </>
              )}
            </dl>
          </div>
        )}

        {activeTab === 'logs' && <AgentLogs logs={logs} agentId={agent.id} />}

        {activeTab === 'metrics' && agent.metrics && (
          <div className="apex-agent-detail__metrics">
            <div className="apex-agent-detail__metric">
              <span className="apex-agent-detail__metric-label">
                Tasks Completed
              </span>
              <span className="apex-agent-detail__metric-value">
                {agent.metrics.tasksCompleted}
              </span>
            </div>
            <div className="apex-agent-detail__metric">
              <span className="apex-agent-detail__metric-label">Tasks Failed</span>
              <span className="apex-agent-detail__metric-value">
                {agent.metrics.tasksFailed}
              </span>
            </div>
            <div className="apex-agent-detail__metric">
              <span className="apex-agent-detail__metric-label">
                Avg Duration
              </span>
              <span className="apex-agent-detail__metric-value">
                {Math.round(agent.metrics.avgTaskDuration / 1000)}s
              </span>
            </div>
            <div className="apex-agent-detail__metric">
              <span className="apex-agent-detail__metric-label">Token Usage</span>
              <span className="apex-agent-detail__metric-value">
                {agent.metrics.tokenUsage.toLocaleString()}
              </span>
            </div>
            <div className="apex-agent-detail__metric">
              <span className="apex-agent-detail__metric-label">
                Est. Cost
              </span>
              <span className="apex-agent-detail__metric-value">
                ${agent.metrics.costEstimate.toFixed(4)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="apex-agent-detail__footer">
        {agent.status === 'running' && (
          <Button variant="danger" onClick={onStop}>
            Stop Agent
          </Button>
        )}
      </div>
    </div>
  );
};
