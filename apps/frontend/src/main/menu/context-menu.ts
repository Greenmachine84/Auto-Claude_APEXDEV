/**
 * APEX Development Platform - Context Menus
 * Phase 4: UI, Integrations & Analytics
 *
 * Provides context menu builders for various UI elements.
 */

import { Menu, MenuItem, BrowserWindow, clipboard, shell } from 'electron';

/** Context menu item */
export interface ContextMenuItem {
  label: string;
  click?: () => void;
  enabled?: boolean;
  visible?: boolean;
  type?: 'normal' | 'separator' | 'submenu' | 'checkbox' | 'radio';
  checked?: boolean;
  submenu?: ContextMenuItem[];
  accelerator?: string;
}

/** Task context menu params */
export interface TaskContextParams {
  taskId: string;
  status: string;
  canCancel: boolean;
  canRetry: boolean;
  canDelete: boolean;
}

/** Agent context menu params */
export interface AgentContextParams {
  agentId: string;
  type: string;
  isRunning: boolean;
}

/** File context menu params */
export interface FileContextParams {
  path: string;
  isDirectory: boolean;
  isGitTracked: boolean;
}

/**
 * Context Menu Builder
 */
export class ContextMenuBuilder {
  private window: BrowserWindow;

  constructor(window: BrowserWindow) {
    this.window = window;
  }

  /**
   * Build task context menu
   */
  public buildTaskMenu(params: TaskContextParams): Menu {
    const { taskId, status, canCancel, canRetry, canDelete } = params;

    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'View Details',
        click: () => this.send('task:view-details', taskId),
      },
      {
        label: 'View Logs',
        click: () => this.send('task:view-logs', taskId),
      },
      { type: 'separator' },
      {
        label: 'Cancel Task',
        enabled: canCancel,
        click: () => this.send('task:cancel', taskId),
      },
      {
        label: 'Retry Task',
        enabled: canRetry,
        click: () => this.send('task:retry', taskId),
      },
      { type: 'separator' },
      {
        label: 'Copy Task ID',
        click: () => clipboard.writeText(taskId),
      },
      { type: 'separator' },
      {
        label: 'Delete Task',
        enabled: canDelete,
        click: () => this.send('task:delete', taskId),
      },
    ];

    return Menu.buildFromTemplate(template);
  }

  /**
   * Build agent context menu
   */
  public buildAgentMenu(params: AgentContextParams): Menu {
    const { agentId, type, isRunning } = params;

    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'View Details',
        click: () => this.send('agent:view-details', agentId),
      },
      {
        label: 'View Logs',
        click: () => this.send('agent:view-logs', agentId),
      },
      { type: 'separator' },
      {
        label: isRunning ? 'Stop Agent' : 'Start Agent',
        click: () => this.send(isRunning ? 'agent:stop' : 'agent:start', agentId),
      },
      {
        label: 'Restart Agent',
        enabled: isRunning,
        click: () => this.send('agent:restart', agentId),
      },
      { type: 'separator' },
      {
        label: 'Configure',
        click: () => this.send('agent:configure', agentId),
      },
      {
        label: 'Copy Agent ID',
        click: () => clipboard.writeText(agentId),
      },
    ];

    return Menu.buildFromTemplate(template);
  }

  /**
   * Build file context menu
   */
  public buildFileMenu(params: FileContextParams): Menu {
    const { path, isDirectory, isGitTracked } = params;

    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: isDirectory ? 'Open Folder' : 'Open File',
        click: () => shell.openPath(path),
      },
      {
        label: 'Reveal in Finder',
        click: () => shell.showItemInFolder(path),
      },
      { type: 'separator' },
      {
        label: 'Copy Path',
        click: () => clipboard.writeText(path),
      },
      {
        label: 'Copy Relative Path',
        click: () => this.send('file:copy-relative-path', path),
      },
      { type: 'separator' },
      ...(isGitTracked
        ? [
            {
              label: 'Git' as const,
              submenu: [
                {
                  label: 'Stage',
                  click: () => this.send('git:stage', path),
                },
                {
                  label: 'Unstage',
                  click: () => this.send('git:unstage', path),
                },
                {
                  label: 'View Diff',
                  click: () => this.send('git:diff', path),
                },
                {
                  label: 'View Blame',
                  click: () => this.send('git:blame', path),
                },
              ],
            } as Electron.MenuItemConstructorOptions,
            { type: 'separator' as const },
          ]
        : []),
      {
        label: 'Delete',
        click: () => this.send('file:delete', path),
      },
    ];

    return Menu.buildFromTemplate(template);
  }

  /**
   * Build terminal context menu
   */
  public buildTerminalMenu(sessionId: string): Menu {
    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'Copy',
        accelerator: 'CmdOrCtrl+C',
        click: () => this.send('terminal:copy', sessionId),
      },
      {
        label: 'Paste',
        accelerator: 'CmdOrCtrl+V',
        click: () => this.send('terminal:paste', sessionId),
      },
      { type: 'separator' },
      {
        label: 'Clear',
        click: () => this.send('terminal:clear', sessionId),
      },
      {
        label: 'Reset',
        click: () => this.send('terminal:reset', sessionId),
      },
      { type: 'separator' },
      {
        label: 'Split Horizontal',
        click: () => this.send('terminal:split-h', sessionId),
      },
      {
        label: 'Split Vertical',
        click: () => this.send('terminal:split-v', sessionId),
      },
      { type: 'separator' },
      {
        label: 'Close Terminal',
        click: () => this.send('terminal:close', sessionId),
      },
    ];

    return Menu.buildFromTemplate(template);
  }

  /**
   * Build generic text context menu
   */
  public buildTextMenu(hasSelection: boolean): Menu {
    const template: Electron.MenuItemConstructorOptions[] = [
      { role: 'cut', enabled: hasSelection },
      { role: 'copy', enabled: hasSelection },
      { role: 'paste' },
      { type: 'separator' },
      { role: 'selectAll' },
    ];

    return Menu.buildFromTemplate(template);
  }

  /**
   * Show context menu at current mouse position
   */
  public showMenu(menu: Menu): void {
    menu.popup({ window: this.window });
  }

  private send(channel: string, data: unknown): void {
    if (!this.window.isDestroyed()) {
      this.window.webContents.send(channel, data);
    }
  }
}

/**
 * Create context menu builder for window
 */
export function createContextMenuBuilder(window: BrowserWindow): ContextMenuBuilder {
  return new ContextMenuBuilder(window);
}
