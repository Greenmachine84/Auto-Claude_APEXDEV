/**
 * APEX Development Platform - LLM Provider Card
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import type { LLMProviderConfig, LLMProviderId } from '../../../preload/api/settings-api';

/** Provider card props */
export interface LLMProviderCardProps {
  id: LLMProviderId;
  name: string;
  icon: string;
  description: string;
  config: LLMProviderConfig;
  isDefault: boolean;
  isExpanded: boolean;
  onToggle: () => void;
  onUpdate: (config: Partial<LLMProviderConfig>) => void;
  onSetDefault: () => void;
}

/**
 * LLM Provider Card Component
 */
export const LLMProviderCard: React.FC<LLMProviderCardProps> = ({
  id,
  name,
  icon,
  description,
  config,
  isDefault,
  isExpanded,
  onToggle,
  onUpdate,
  onSetDefault,
}) => {
  const [apiKeyVisible, setApiKeyVisible] = React.useState(false);

  // Get field config based on provider
  const getProviderFields = () => {
    switch (id) {
      case 'copilot':
        return null; // Copilot uses VS Code auth
      case 'ollama':
      case 'lmstudio':
        return (
          <>
            <div className="apex-llm-card__field">
              <label>Base URL</label>
              <Input
                value={config.baseUrl || 'http://localhost:11434'}
                onChange={(e) => onUpdate({ baseUrl: e.target.value })}
                placeholder="http://localhost:11434"
              />
            </div>
            <div className="apex-llm-card__field">
              <label>Model</label>
              <Input
                value={config.model || ''}
                onChange={(e) => onUpdate({ model: e.target.value })}
                placeholder="llama3, codellama, etc."
              />
            </div>
          </>
        );
      case 'azure':
        return (
          <>
            <div className="apex-llm-card__field">
              <label>API Key</label>
              <div className="apex-llm-card__secret">
                <Input
                  type={apiKeyVisible ? 'text' : 'password'}
                  value={config.apiKey || ''}
                  onChange={(e) => onUpdate({ apiKey: e.target.value })}
                  placeholder="Your Azure API key"
                />
                <button onClick={() => setApiKeyVisible(!apiKeyVisible)}>
                  {apiKeyVisible ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
            <div className="apex-llm-card__field">
              <label>Endpoint</label>
              <Input
                value={config.baseUrl || ''}
                onChange={(e) => onUpdate({ baseUrl: e.target.value })}
                placeholder="https://your-resource.openai.azure.com"
              />
            </div>
            <div className="apex-llm-card__field">
              <label>Deployment Name</label>
              <Input
                value={config.deploymentName || ''}
                onChange={(e) => onUpdate({ deploymentName: e.target.value })}
                placeholder="gpt-4-deployment"
              />
            </div>
          </>
        );
      default:
        return (
          <>
            <div className="apex-llm-card__field">
              <label>API Key</label>
              <div className="apex-llm-card__secret">
                <Input
                  type={apiKeyVisible ? 'text' : 'password'}
                  value={config.apiKey || ''}
                  onChange={(e) => onUpdate({ apiKey: e.target.value })}
                  placeholder={`Your ${name} API key`}
                />
                <button onClick={() => setApiKeyVisible(!apiKeyVisible)}>
                  {apiKeyVisible ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
            {id === 'openrouter' && (
              <div className="apex-llm-card__field">
                <label>Model</label>
                <Input
                  value={config.model || ''}
                  onChange={(e) => onUpdate({ model: e.target.value })}
                  placeholder="anthropic/claude-3-opus"
                />
              </div>
            )}
          </>
        );
    }
  };

  return (
    <div
      className={`apex-llm-card ${
        config.enabled ? 'apex-llm-card--enabled' : 'apex-llm-card--disabled'
      } ${isDefault ? 'apex-llm-card--default' : ''}`}
    >
      {/* Header */}
      <div className="apex-llm-card__header" onClick={onToggle}>
        <span className="apex-llm-card__icon">{icon}</span>
        <div className="apex-llm-card__info">
          <h5>{name}</h5>
          <span>{description}</span>
        </div>
        <div className="apex-llm-card__status">
          {isDefault && <span className="apex-llm-card__badge">★ Default</span>}
          <label className="apex-llm-card__toggle">
            <input
              type="checkbox"
              checked={config.enabled || false}
              onChange={(e) => {
                e.stopPropagation();
                onUpdate({ enabled: e.target.checked });
              }}
            />
            <span className="apex-llm-card__toggle-slider" />
          </label>
        </div>
        <span className="apex-llm-card__expand">{isExpanded ? '▲' : '▼'}</span>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="apex-llm-card__content">
          {id === 'copilot' ? (
            <p className="apex-llm-card__note">
              📝 GitHub Copilot uses VS Code authentication. Ensure you&apos;re signed in.
            </p>
          ) : (
            getProviderFields()
          )}
          
          {config.enabled && !isDefault && (
            <Button variant="ghost" onClick={onSetDefault}>
              Set as Default
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
