/**
 * APEX Development Platform - General Settings
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Select, type SelectOption } from '../common/Select';
import { Input } from '../common/Input';
import type { Settings } from '../../../preload/api/settings-api';

/** General settings props */
export interface GeneralSettingsProps {
  settings: Settings;
  onUpdate: (updates: Partial<Settings>) => void;
}

/** Theme options */
const themeOptions: SelectOption<'light' | 'dark' | 'system'>[] = [
  { value: 'system', label: '💻 System' },
  { value: 'light', label: '☀️ Light' },
  { value: 'dark', label: '🌙 Dark' },
];

/** Language options */
const languageOptions: SelectOption<string>[] = [
  { value: 'en', label: '🇺🇸 English' },
  { value: 'es', label: '🇪🇸 Español' },
  { value: 'fr', label: '🇫🇷 Français' },
  { value: 'de', label: '🇩🇪 Deutsch' },
  { value: 'ja', label: '🇯🇵 日本語' },
  { value: 'zh', label: '🇨🇳 中文' },
];

/**
 * General Settings Component
 */
export const GeneralSettings: React.FC<GeneralSettingsProps> = ({
  settings,
  onUpdate,
}) => {
  return (
    <div className="apex-settings-section">
      <h3>⚙️ General Settings</h3>

      {/* Appearance */}
      <div className="apex-settings-group">
        <h4>Appearance</h4>
        <div className="apex-settings-field">
          <label>Theme</label>
          <Select
            options={themeOptions}
            value={settings.theme}
            onChange={(val) => onUpdate({ theme: val as 'light' | 'dark' | 'system' })}
          />
        </div>
        <div className="apex-settings-field">
          <label>Language</label>
          <Select
            options={languageOptions}
            value={settings.language || 'en'}
            onChange={(val) => onUpdate({ language: val })}
          />
        </div>
        <div className="apex-settings-field">
          <label>Font Size</label>
          <input
            type="range"
            min="12"
            max="20"
            value={settings.fontSize || 14}
            onChange={(e) => onUpdate({ fontSize: parseInt(e.target.value) })}
          />
          <span>{settings.fontSize || 14}px</span>
        </div>
      </div>

      {/* Editor */}
      <div className="apex-settings-group">
        <h4>Editor</h4>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="autoSave"
            checked={settings.autoSave ?? true}
            onChange={(e) => onUpdate({ autoSave: e.target.checked })}
          />
          <label htmlFor="autoSave">Auto-save changes</label>
        </div>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="wordWrap"
            checked={settings.wordWrap ?? true}
            onChange={(e) => onUpdate({ wordWrap: e.target.checked })}
          />
          <label htmlFor="wordWrap">Word wrap</label>
        </div>
        <div className="apex-settings-field">
          <label>Tab Size</label>
          <input
            type="number"
            min="2"
            max="8"
            value={settings.tabSize || 2}
            onChange={(e) => onUpdate({ tabSize: parseInt(e.target.value) })}
          />
        </div>
      </div>

      {/* Workspace */}
      <div className="apex-settings-group">
        <h4>Workspace</h4>
        <div className="apex-settings-field">
          <label>Default Project Path</label>
          <Input
            value={settings.defaultProjectPath || ''}
            onChange={(e) => onUpdate({ defaultProjectPath: e.target.value })}
            placeholder="~/projects"
          />
        </div>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="openLastProject"
            checked={settings.openLastProject ?? true}
            onChange={(e) => onUpdate({ openLastProject: e.target.checked })}
          />
          <label htmlFor="openLastProject">Reopen last project on startup</label>
        </div>
      </div>

      {/* Notifications */}
      <div className="apex-settings-group">
        <h4>Notifications</h4>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="notifications"
            checked={typeof settings.notifications === "boolean" ? settings.notifications : settings.notifications?.enabled ?? true}
            onChange={(e) => onUpdate({ notifications: e.target.checked })}
          />
          <label htmlFor="notifications">Enable desktop notifications</label>
        </div>
        <div className="apex-settings-field apex-settings-field--checkbox">
          <input
            type="checkbox"
            id="sounds"
            checked={settings.sounds ?? false}
            onChange={(e) => onUpdate({ sounds: e.target.checked })}
          />
          <label htmlFor="sounds">Enable sound effects</label>
        </div>
      </div>
    </div>
  );
};

