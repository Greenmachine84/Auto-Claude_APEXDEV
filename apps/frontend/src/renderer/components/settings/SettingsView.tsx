/**
 * APEX Development Platform - Settings View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import { GeneralSettings } from './GeneralSettings';
import { LLMSettings } from './LLMSettings';
import { AgentSettings } from './AgentSettings';
import { IntegrationSettings } from './IntegrationSettings';
import { KeybindSettings } from './KeybindSettings';
import { useSettings } from '../../hooks/useSettings';

/** Settings sections */
type SettingsSection = 'general' | 'llm' | 'agents' | 'integrations' | 'keybinds';

/** Section config */
const sections: { id: SettingsSection; icon: string; label: string }[] = [
  { id: 'general', icon: '⚙️', label: 'General' },
  { id: 'llm', icon: '🤖', label: 'LLM Providers' },
  { id: 'agents', icon: '👤', label: 'Agents' },
  { id: 'integrations', icon: '🔗', label: 'Integrations' },
  { id: 'keybinds', icon: '⌨️', label: 'Keybinds' },
];

/**
 * Settings View Component
 */
const SettingsView: React.FC = () => {
  const [activeSection, setActiveSection] = useState<SettingsSection>('general');
  const { settings, updateSettings, resetSettings, loading, error } = useSettings();

  if (loading) {
    return <div className="apex-settings-view apex-settings-view--loading">Loading...</div>;
  }

  if (error) {
    return (
      <div className="apex-settings-view apex-settings-view--error">
        Error loading settings: {error.message}
      </div>
    );
  }

  return (
    <div className="apex-settings-view">
      {/* Sidebar */}
      <nav className="apex-settings-view__nav">
        <h2>⚙️ Settings</h2>
        <ul>
          {sections.map((section) => (
            <li key={section.id}>
              <button
                className={`apex-settings-view__nav-item ${
                  activeSection === section.id ? 'apex-settings-view__nav-item--active' : ''
                }`}
                onClick={() => setActiveSection(section.id)}
              >
                <span>{section.icon}</span>
                <span>{section.label}</span>
              </button>
            </li>
          ))}
        </ul>
        <button
          className="apex-settings-view__reset"
          onClick={() => {
            if (window.confirm('Reset all settings to defaults?')) {
              resetSettings();
            }
          }}
        >
          ↺ Reset All
        </button>
      </nav>

      {/* Content */}
      <div className="apex-settings-view__content">
        {activeSection === 'general' && (
          <GeneralSettings settings={settings as any} onUpdate={updateSettings} />
        )}
        {activeSection === 'llm' && (
          <LLMSettings settings={settings as any} onUpdate={updateSettings} />
        )}
        {activeSection === 'agents' && (
          <AgentSettings settings={settings as any} onUpdate={updateSettings} />
        )}
        {activeSection === 'integrations' && (
          <IntegrationSettings settings={settings as any} onSettingsChange={(s: any) => updateSettings(s)} isOpen={true} />
        )}
        {activeSection === 'keybinds' && (
          <KeybindSettings settings={settings as any} onUpdate={updateSettings} />
        )}
      </div>
    </div>
  );
};

export default SettingsView;


