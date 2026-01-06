/**
 * APEX Development Platform - Integration Settings
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import type { Settings } from '../../../preload/api/settings-api';

/** Integration settings props */
export interface IntegrationSettingsProps {
  settings: Settings;
  onUpdate: (updates: Partial<Settings>) => void;
}

/** Integration metadata */
type IntegrationId = 'github' | 'gitlab' | 'linear' | 'slack' | 'jira';

const integrations: { id: IntegrationId; icon: string; name: string; description: string }[] = [
  { id: 'github', icon: '🐙', name: 'GitHub', description: 'Pull requests, issues, and code review' },
  { id: 'gitlab', icon: '🧑', name: 'GitLab', description: 'Merge requests and CI/CD integration' },
  { id: 'linear', icon: '📊', name: 'Linear', description: 'Issue tracking and project management' },
  { id: 'slack', icon: '💬', name: 'Slack', description: 'Notifications and team communication' },
  { id: 'jira', icon: '📃', name: 'JIRA', description: 'Issue tracking and agile boards' },
];

/**
 * Integration Settings Component
 */
export const IntegrationSettings: React.FC<IntegrationSettingsProps> = ({
  settings,
  onUpdate,
}) => {
  const [expandedId, setExpandedId] = useState<IntegrationId | null>(null);
  const [tokenVisible, setTokenVisible] = useState<Record<string, boolean>>({});

  const integrationConfigs = settings.integrations || {};

  const updateIntegration = (id: IntegrationId, config: Record<string, unknown>) => {
    onUpdate({
      integrations: {
        ...integrationConfigs,
        [id]: { ...integrationConfigs[id], ...config },
      },
    });
  };

  const testConnection = async (id: IntegrationId) => {
    // Placeholder for connection test
    alert(`Testing ${id} connection... (Not implemented)`);
  };

  return (
    <div className="apex-settings-section">
      <h3>🔗 Integration Settings</h3>
      <p className="apex-settings-description">
        Connect external services for enhanced workflow automation.
      </p>

      <div className="apex-integration-settings__list">
        {integrations.map(({ id, icon, name, description }) => {
          const config = integrationConfigs[id] || {};
          const isExpanded = expandedId === id;

          return (
            <div
              key={id}
              className={`apex-integration-card ${
                config.enabled ? 'apex-integration-card--enabled' : ''
              }`}
            >
              {/* Header */}
              <div
                className="apex-integration-card__header"
                onClick={() => setExpandedId(isExpanded ? null : id)}
              >
                <span className="apex-integration-card__icon">{icon}</span>
                <div className="apex-integration-card__info">
                  <h5>{name}</h5>
                  <span>{description}</span>
                </div>
                <label className="apex-integration-card__toggle">
                  <input
                    type="checkbox"
                    checked={config.enabled || false}
                    onChange={(e) => {
                      e.stopPropagation();
                      updateIntegration(id, { enabled: e.target.checked });
                    }}
                  />
                  <span className="apex-integration-card__toggle-slider" />
                </label>
                <span className="apex-integration-card__expand">
                  {isExpanded ? '▲' : '▼'}
                </span>
              </div>

              {/* Content */}
              {isExpanded && (
                <div className="apex-integration-card__content">
                  {id === 'github' && (
                    <>
                      <div className="apex-integration-card__field">
                        <label>Personal Access Token</label>
                        <div className="apex-integration-card__secret">
                          <Input
                            type={tokenVisible[id] ? 'text' : 'password'}
                            value={config.token || ''}
                            onChange={(e) => updateIntegration(id, { token: e.target.value })}
                            placeholder="ghp_..."
                          />
                          <button onClick={() => setTokenVisible({ ...tokenVisible, [id]: !tokenVisible[id] })}>
                            {tokenVisible[id] ? '🙈' : '👁️'}
                          </button>
                        </div>
                      </div>
                      <div className="apex-integration-card__field">
                        <label>Default Owner</label>
                        <Input
                          value={config.owner || ''}
                          onChange={(e) => updateIntegration(id, { owner: e.target.value })}
                          placeholder="username or org"
                        />
                      </div>
                    </>
                  )}

                  {id === 'gitlab' && (
                    <>
                      <div className="apex-integration-card__field">
                        <label>GitLab URL</label>
                        <Input
                          value={config.url || 'https://gitlab.com'}
                          onChange={(e) => updateIntegration(id, { url: e.target.value })}
                          placeholder="https://gitlab.com"
                        />
                      </div>
                      <div className="apex-integration-card__field">
                        <label>Access Token</label>
                        <div className="apex-integration-card__secret">
                          <Input
                            type={tokenVisible[id] ? 'text' : 'password'}
                            value={config.token || ''}
                            onChange={(e) => updateIntegration(id, { token: e.target.value })}
                            placeholder="glpat-..."
                          />
                          <button onClick={() => setTokenVisible({ ...tokenVisible, [id]: !tokenVisible[id] })}>
                            {tokenVisible[id] ? '🙈' : '👁️'}
                          </button>
                        </div>
                      </div>
                    </>
                  )}

                  {id === 'linear' && (
                    <div className="apex-integration-card__field">
                      <label>API Key</label>
                      <div className="apex-integration-card__secret">
                        <Input
                          type={tokenVisible[id] ? 'text' : 'password'}
                          value={config.apiKey || ''}
                          onChange={(e) => updateIntegration(id, { apiKey: e.target.value })}
                          placeholder="lin_api_..."
                        />
                        <button onClick={() => setTokenVisible({ ...tokenVisible, [id]: !tokenVisible[id] })}>
                          {tokenVisible[id] ? '🙈' : '👁️'}
                        </button>
                      </div>
                    </div>
                  )}

                  {id === 'slack' && (
                    <>
                      <div className="apex-integration-card__field">
                        <label>Webhook URL</label>
                        <Input
                          value={config.webhookUrl || ''}
                          onChange={(e) => updateIntegration(id, { webhookUrl: e.target.value })}
                          placeholder="https://hooks.slack.com/services/..."
                        />
                      </div>
                      <div className="apex-integration-card__field">
                        <label>Default Channel</label>
                        <Input
                          value={config.channel || ''}
                          onChange={(e) => updateIntegration(id, { channel: e.target.value })}
                          placeholder="#dev-notifications"
                        />
                      </div>
                    </>
                  )}

                  {id === 'jira' && (
                    <>
                      <div className="apex-integration-card__field">
                        <label>JIRA URL</label>
                        <Input
                          value={config.url || ''}
                          onChange={(e) => updateIntegration(id, { url: e.target.value })}
                          placeholder="https://yourcompany.atlassian.net"
                        />
                      </div>
                      <div className="apex-integration-card__field">
                        <label>Email</label>
                        <Input
                          value={config.email || ''}
                          onChange={(e) => updateIntegration(id, { email: e.target.value })}
                          placeholder="your@email.com"
                        />
                      </div>
                      <div className="apex-integration-card__field">
                        <label>API Token</label>
                        <div className="apex-integration-card__secret">
                          <Input
                            type={tokenVisible[id] ? 'text' : 'password'}
                            value={config.apiToken || ''}
                            onChange={(e) => updateIntegration(id, { apiToken: e.target.value })}
                            placeholder="Your JIRA API token"
                          />
                          <button onClick={() => setTokenVisible({ ...tokenVisible, [id]: !tokenVisible[id] })}>
                            {tokenVisible[id] ? '🙈' : '👁️'}
                          </button>
                        </div>
                      </div>
                    </>
                  )}

                  <div className="apex-integration-card__actions">
                    <Button variant="ghost" onClick={() => testConnection(id)}>
                      🔌 Test Connection
                    </Button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
