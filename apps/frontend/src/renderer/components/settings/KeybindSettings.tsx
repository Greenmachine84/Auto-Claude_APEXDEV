/**
 * APEX Development Platform - Keybind Settings
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import { Button } from '../common/Button';
import type { Settings } from '../../../preload/api/settings-api';

/** Keybind settings props */
export interface KeybindSettingsProps {
  settings: Settings;
  onUpdate: (updates: Partial<Settings>) => void;
}

/** Default keybinds */
const defaultKeybinds: Record<string, { key: string; description: string }> = {
  newTask: { key: 'Ctrl+N', description: 'Create new task' },
  openCommand: { key: 'Ctrl+Shift+P', description: 'Open command palette' },
  toggleSidebar: { key: 'Ctrl+B', description: 'Toggle sidebar' },
  runAgent: { key: 'Ctrl+Enter', description: 'Run selected agent' },
  stopAgent: { key: 'Ctrl+Shift+C', description: 'Stop running agent' },
  switchTab: { key: 'Ctrl+Tab', description: 'Switch tab' },
  closeTab: { key: 'Ctrl+W', description: 'Close current tab' },
  find: { key: 'Ctrl+F', description: 'Find in view' },
  settings: { key: 'Ctrl+,', description: 'Open settings' },
  terminal: { key: 'Ctrl+`', description: 'Toggle terminal' },
};

/**
 * Keybind Settings Component
 */
export const KeybindSettings: React.FC<KeybindSettingsProps> = ({
  settings,
  onUpdate,
}) => {
  const [recording, setRecording] = useState<string | null>(null);
  const [recordedKeys, setRecordedKeys] = useState<string[]>([]);

  const keybinds = settings.keybinds || {};

  const getKeybind = (action: string) => {
    return keybinds[action] || defaultKeybinds[action]?.key || '';
  };

  const handleStartRecording = (action: string) => {
    setRecording(action);
    setRecordedKeys([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent, action: string) => {
    if (recording !== action) return;

    e.preventDefault();
    e.stopPropagation();

    const keys: string[] = [];
    if (e.ctrlKey) keys.push('Ctrl');
    if (e.shiftKey) keys.push('Shift');
    if (e.altKey) keys.push('Alt');
    if (e.metaKey) keys.push('Meta');
    if (e.key && !['Control', 'Shift', 'Alt', 'Meta'].includes(e.key)) {
      keys.push(e.key.length === 1 ? e.key.toUpperCase() : e.key);
    }

    setRecordedKeys(keys);
  };

  const handleSaveKeybind = (action: string) => {
    if (recordedKeys.length > 0) {
      onUpdate({
        keybinds: {
          ...keybinds,
          [action]: recordedKeys.join('+'),
        },
      });
    }
    setRecording(null);
    setRecordedKeys([]);
  };

  const handleResetKeybind = (action: string) => {
    const newKeybinds = { ...keybinds };
    delete newKeybinds[action];
    onUpdate({ keybinds: newKeybinds });
  };

  const handleResetAll = () => {
    if (window.confirm('Reset all keybinds to defaults?')) {
      onUpdate({ keybinds: {} });
    }
  };

  return (
    <div className="apex-settings-section">
      <h3>⌨️ Keyboard Shortcuts</h3>
      <p className="apex-settings-description">
        Customize keyboard shortcuts for common actions.
      </p>

      <div className="apex-keybind-settings__actions">
        <Button variant="ghost" onClick={handleResetAll}>
          ↺ Reset All to Defaults
        </Button>
      </div>

      <div className="apex-keybind-settings__list">
        {Object.entries(defaultKeybinds).map(([action, { description }]) => {
          const isRecording = recording === action;
          const currentKey = getKeybind(action);
          const isCustom = keybinds[action] !== undefined;

          return (
            <div
              key={action}
              className={`apex-keybind-item ${
                isRecording ? 'apex-keybind-item--recording' : ''
              }`}
            >
              <div className="apex-keybind-item__info">
                <span className="apex-keybind-item__description">{description}</span>
                {isCustom && (
                  <span className="apex-keybind-item__badge">Custom</span>
                )}
              </div>

              <div className="apex-keybind-item__key">
                {isRecording ? (
                  <input
                    type="text"
                    className="apex-keybind-item__input"
                    placeholder="Press keys..."
                    value={recordedKeys.join('+')}
                    onKeyDown={(e) => handleKeyDown(e, action)}
                    autoFocus
                    readOnly
                  />
                ) : (
                  <kbd
                    className="apex-keybind-item__kbd"
                    onClick={() => handleStartRecording(action)}
                  >
                    {currentKey}
                  </kbd>
                )}
              </div>

              <div className="apex-keybind-item__actions">
                {isRecording ? (
                  <>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleSaveKeybind(action)}
                    >
                      Save
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setRecording(null)}
                    >
                      Cancel
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleStartRecording(action)}
                    >
                      Edit
                    </Button>
                    {isCustom && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleResetKeybind(action)}
                      >
                        Reset
                      </Button>
                    )}
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="apex-keybind-settings__note">
        <p>
          <strong>Note:</strong> Some shortcuts may conflict with browser or OS shortcuts.
          Use <kbd>Ctrl</kbd> + <kbd>Shift</kbd> combinations for best compatibility.
        </p>
      </div>
    </div>
  );
};
