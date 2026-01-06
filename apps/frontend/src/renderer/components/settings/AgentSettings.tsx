/**
 * APEX Development Platform - Agent Settings
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Select, type SelectOption } from '../common/Select';
import type { Settings } from '../../../preload/api/settings-api';

/** Agent settings props */
export interface AgentSettingsProps {
  settings: Settings;
  onUpdate: (updates: Partial<Settings>) => void;
}

/** Agent type options */
const agentTypeOptions: SelectOption<string>[] = [
  { value: 'coder', label: '💻 Coder' },
  { value: 'reviewer', label: '🔍 Reviewer' },
  { value: 'fixer', label: '🔧 Fixer' },
  { value: 'planner', label: '📝 Planner' },
  { value: 'analyst', label: '📊 Analyst' },
];

/**
 * Agent Settings Component
 */
export const AgentSettings: React.FC<AgentSettingsProps> = ({
  settings,
  onUpdate,
}) => {
  const agentConfig = settings.agentConfig || {};

  const updateAgentConfig = (key: string, value: unknown) => {
    onUpdate({
      agentConfig: {
        ...agentConfig,
        [key]: value,
      },
    });
  };

  return (
    <div className="apex-settings-section">
      <h3>👤 Agent Settings</h3>

      {/* Pool Configuration */}
      <div className="apex-settings-group">
        <h4>Agent Pool</h4>
        <div className="apex-settings-field">
          <label>Max Concurrent Agents</label>
          <input
            type="number"
            min="1"
            max="10"
            value={agentConfig.maxConcurrent || 3}
            onChange={(e) => updateAgentConfig('maxConcurrent', parseInt(e.target.value))}
          />
        </div>
        <div className="apex-settings-field">
          <label>Agent Timeout (seconds)</label>
          <input
            type="number"
            min="30"
            max="3600"
            value={agentConfig.timeout || 300}
            onChange={(e) => updateAgentConfig('timeout', parseInt(e.target.value))}
          />
        </div>
        <div className="apex-settings-field">
          <label>Default Agent Type</label>
          <Select
            options={agentTypeOptions}
            value={agentConfig.defaultType || 'coder'}
            onChange={(val) => updateAgentConfig('defaultType', val)}
          />
        </div>
      </div>

      {/* Behavior */}
      <div className="apex-settings-group">
        <h4>Behavior</h4>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="autoRetry"
            checked={agentConfig.autoRetry ?? true}
            onChange={(e) => updateAgentConfig('autoRetry', e.target.checked)}
          />
          <label htmlFor="autoRetry">Auto-retry on failure</label>
        </div>
        <div className="apex-settings-field">
          <label>Max Retries</label>
          <input
            type="number"
            min="0"
            max="5"
            value={agentConfig.maxRetries || 3}
            onChange={(e) => updateAgentConfig('maxRetries', parseInt(e.target.value))}
          />
        </div>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="verbose"
            checked={agentConfig.verbose ?? false}
            onChange={(e) => updateAgentConfig('verbose', e.target.checked)}
          />
          <label htmlFor="verbose">Verbose logging</label>
        </div>
      </div>

      {/* Memory */}
      <div className="apex-settings-group">
        <h4>Memory</h4>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="useMemory"
            checked={agentConfig.useMemory ?? true}
            onChange={(e) => updateAgentConfig('useMemory', e.target.checked)}
          />
          <label htmlFor="useMemory">Enable episodic memory</label>
        </div>
        <div className="apex-settings-field">
          <label>Memory Context Length</label>
          <input
            type="number"
            min="1"
            max="50"
            value={agentConfig.memoryContextLength || 10}
            onChange={(e) => updateAgentConfig('memoryContextLength', parseInt(e.target.value))}
          />
        </div>
        <div className="apex-settings-field">
          <label>Similarity Threshold</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={agentConfig.similarityThreshold || 0.7}
            onChange={(e) => updateAgentConfig('similarityThreshold', parseFloat(e.target.value))}
          />
          <span>{(agentConfig.similarityThreshold || 0.7).toFixed(1)}</span>
        </div>
      </div>

      {/* Approval */}
      <div className="apex-settings-group">
        <h4>Approval Workflow</h4>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="requireApproval"
            checked={agentConfig.requireApproval ?? false}
            onChange={(e) => updateAgentConfig('requireApproval', e.target.checked)}
          />
          <label htmlFor="requireApproval">Require approval for destructive actions</label>
        </div>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="notifyOnComplete"
            checked={agentConfig.notifyOnComplete ?? true}
            onChange={(e) => updateAgentConfig('notifyOnComplete', e.target.checked)}
          />
          <label htmlFor="notifyOnComplete">Notify when agent completes</label>
        </div>
      </div>
    </div>
  );
};
