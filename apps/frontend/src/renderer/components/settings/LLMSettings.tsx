/**
 * APEX Development Platform - LLM Settings
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import { LLMProviderCard } from './LLMProviderCard';
import { Select, type SelectOption } from '../common/Select';
import type { Settings, LLMProviderConfig, LLMProviderId } from '../../../preload/api/settings-api';

/** LLM settings props */
export interface LLMSettingsProps {
  settings: Settings;
  onUpdate: (updates: Partial<Settings>) => void;
}

/** Provider metadata */
const providerMeta: Record<LLMProviderId, { name: string; icon: string; description: string }> = {
  copilot: { name: 'GitHub Copilot', icon: '🐙', description: 'VS Code integrated AI assistant' },
  openrouter: { name: 'OpenRouter', icon: '🌐', description: 'Multi-provider API gateway' },
  ollama: { name: 'Ollama', icon: '🧬', description: 'Local open-source models' },
  lmstudio: { name: 'LM Studio', icon: '💻', description: 'Local model runtime' },
  gemini: { name: 'Google Gemini', icon: '✨', description: 'Google AI models' },
  openai: { name: 'OpenAI', icon: '🧠', description: 'GPT-4 and beyond' },
  anthropic: { name: 'Anthropic', icon: '🤖', description: 'Claude models' },
  azure: { name: 'Azure OpenAI', icon: '☁️', description: 'Enterprise OpenAI' },
};

/** All provider IDs */
const allProviders: LLMProviderId[] = [
  'copilot', 'openrouter', 'ollama', 'lmstudio', 'gemini', 'openai', 'anthropic', 'azure'
];

/**
 * LLM Settings Component
 */
export const LLMSettings: React.FC<LLMSettingsProps> = ({ settings, onUpdate }) => {
  const [expandedProvider, setExpandedProvider] = useState<LLMProviderId | null>(null);

  // Get provider configs
  const providers = (settings.llmProviders || {}) as Record<LLMProviderId, LLMProviderConfig>;

  // Update a specific provider
  const updateProvider = (id: LLMProviderId, config: Partial<LLMProviderConfig>) => {
    onUpdate({
      llmProviders: {
        ...providers,
        [id]: { ...providers[id], ...config },
      },
    });
  };

  // Set default provider
  const setDefaultProvider = (id: LLMProviderId) => {
    onUpdate({ defaultLLMProvider: id });
  };

  // Default provider options
  const defaultProviderOptions: SelectOption<LLMProviderId>[] = allProviders
    .filter((id) => providers[id]?.enabled)
    .map((id) => ({
      value: id,
      label: `${providerMeta[id].icon} ${providerMeta[id].name}`,
    }));

  return (
    <div className="apex-settings-section">
      <h3>🤖 LLM Providers</h3>
      <p className="apex-settings-description">
        Configure AI model providers for code generation, review, and agent tasks.
      </p>

      {/* Default Provider */}
      <div className="apex-settings-group">
        <h4>Default Provider</h4>
        <div className="apex-settings-field">
          <label>Primary LLM Provider</label>
          <Select
            options={defaultProviderOptions}
            value={settings.defaultLLMProvider || 'copilot'}
            onChange={(val) => setDefaultProvider(val as LLMProviderId)}
            placeholder="Select default provider"
          />
        </div>
      </div>

      {/* Provider Cards */}
      <div className="apex-settings-group">
        <h4>Available Providers</h4>
        <div className="apex-llm-settings__providers">
          {allProviders.map((id) => (
            <LLMProviderCard
              key={id}
              id={id}
              name={providerMeta[id].name}
              icon={providerMeta[id].icon}
              description={providerMeta[id].description}
              config={providers[id] || { enabled: false }}
              isDefault={settings.defaultLLMProvider === id}
              isExpanded={expandedProvider === id}
              onToggle={() =>
                setExpandedProvider(expandedProvider === id ? null : id)
              }
              onUpdate={(config) => updateProvider(id, config)}
              onSetDefault={() => setDefaultProvider(id)}
            />
          ))}
        </div>
      </div>

      {/* Model Selection */}
      <div className="apex-settings-group">
        <h4>Model Preferences</h4>
        <div className="apex-settings-field">
          <label>Preferred Model (when available)</label>
          <Select
            options={[
              { value: 'auto', label: '🎯 Auto (Provider Default)' },
              { value: 'fast', label: '⚡ Fast (Lower latency)' },
              { value: 'balanced', label: '⚖️ Balanced' },
              { value: 'quality', label: '🌟 Quality (Best output)' },
            ]}
            value={settings.modelPreference || 'auto'}
            onChange={(val) => onUpdate({ modelPreference: val })}
          />
        </div>
        <div className="apex-settings-field">
          <label>Max Tokens</label>
          <input
            type="number"
            min="256"
            max="128000"
            step="256"
            value={(settings.maxTokens as number) || 4096}
            onChange={(e) => onUpdate({ maxTokens: parseInt(e.target.value) })}
          />
        </div>
        <div className="apex-settings-field">
          <label>Temperature</label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={(settings.temperature as number) || 0.7}
            onChange={(e) => onUpdate({ temperature: parseFloat(e.target.value) })}
          />
          <span>{((settings.temperature as number) || 0.7).toFixed(1)}</span>
        </div>
      </div>
    </div>
  );
};


