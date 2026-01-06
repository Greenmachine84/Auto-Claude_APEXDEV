/**
 * APEX Development Platform - Application Menu
 * Phase 4: UI, Integrations & Analytics
 *
 * Defines the native application menu structure.
 */

import { Menu, MenuItem, BrowserWindow, app, shell, dialog } from 'electron';
import { WindowManager } from '../window-manager';
import { AppLifecycle } from '../app';

/**
 * Build and set application menu
 */
export function buildAppMenu(): Menu {
  const isMac = process.platform === 'darwin';
  const windowManager = WindowManager.getInstance();

  const template: (Electron.MenuItemConstructorOptions | MenuItem)[] = [
    // App menu (macOS only)
    ...(isMac
      ? [
          {
            label: app.name,
            submenu: [
              { role: 'about' as const },
              { type: 'separator' as const },
              {
                label: 'Preferences...',
                accelerator: 'Cmd+,',
                click: () => windowManager.createSettingsWindow(),
              },
              { type: 'separator' as const },
              { role: 'services' as const },
              { type: 'separator' as const },
              { role: 'hide' as const },
              { role: 'hideOthers' as const },
              { role: 'unhide' as const },
              { type: 'separator' as const },
              { role: 'quit' as const },
            ],
          },
        ]
      : []),

    // File menu
    {
      label: 'File',
      submenu: [
        {
          label: 'New Task',
          accelerator: 'CmdOrCtrl+N',
          click: () => sendToRenderer('menu:new-task'),
        },
        {
          label: 'Open Project...',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog({
              properties: ['openDirectory'],
              title: 'Open Project',
            });
            if (!result.canceled && result.filePaths[0]) {
              sendToRenderer('menu:open-project', result.filePaths[0]);
            }
          },
        },
        { type: 'separator' },
        {
          label: 'Save',
          accelerator: 'CmdOrCtrl+S',
          click: () => sendToRenderer('menu:save'),
        },
        { type: 'separator' },
        ...(isMac ? [] : [{ role: 'quit' as const }]),
      ],
    },

    // Edit menu
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' },
        ...(isMac
          ? [
              { type: 'separator' as const },
              {
                label: 'Speech',
                submenu: [
                  { role: 'startSpeaking' as const },
                  { role: 'stopSpeaking' as const },
                ],
              },
            ]
          : []),
      ],
    },

    // View menu
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        {
          label: 'Toggle Sidebar',
          accelerator: 'CmdOrCtrl+B',
          click: () => sendToRenderer('menu:toggle-sidebar'),
        },
        {
          label: 'Toggle Terminal',
          accelerator: 'CmdOrCtrl+`',
          click: () => sendToRenderer('menu:toggle-terminal'),
        },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },

    // Agents menu
    {
      label: 'Agents',
      submenu: [
        {
          label: 'Start Coder Agent',
          accelerator: 'CmdOrCtrl+Shift+C',
          click: () => sendToRenderer('menu:start-agent', 'coder'),
        },
        {
          label: 'Start Reviewer Agent',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => sendToRenderer('menu:start-agent', 'reviewer'),
        },
        {
          label: 'Start Fixer Agent',
          accelerator: 'CmdOrCtrl+Shift+F',
          click: () => sendToRenderer('menu:start-agent', 'fixer'),
        },
        {
          label: 'Start Planner Agent',
          accelerator: 'CmdOrCtrl+Shift+P',
          click: () => sendToRenderer('menu:start-agent', 'planner'),
        },
        { type: 'separator' },
        {
          label: 'Stop All Agents',
          click: () => sendToRenderer('menu:stop-all-agents'),
        },
        { type: 'separator' },
        {
          label: 'Agent Pool Status',
          click: () => sendToRenderer('menu:show-pool-status'),
        },
      ],
    },

    // Window menu
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        ...(isMac
          ? [
              { type: 'separator' as const },
              { role: 'front' as const },
              { type: 'separator' as const },
              { role: 'window' as const },
            ]
          : [{ role: 'close' as const }]),
      ],
    },

    // Help menu
    {
      role: 'help',
      submenu: [
        {
          label: 'Documentation',
          click: () => shell.openExternal('https://github.com/apex/docs'),
        },
        {
          label: 'Report Issue',
          click: () => shell.openExternal('https://github.com/apex/issues'),
        },
        { type: 'separator' },
        {
          label: 'View Logs',
          click: () => sendToRenderer('menu:show-logs'),
        },
        {
          label: 'About APEX',
          click: () => {
            dialog.showMessageBox({
              type: 'info',
              title: 'About APEX',
              message: 'APEX Development Platform',
              detail: `Version: ${app.getVersion()}\nElectron: ${process.versions.electron}\nNode: ${process.versions.node}`,
            });
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  return menu;
}

/**
 * Send message to renderer
 */
function sendToRenderer(channel: string, data?: unknown): void {
  const mainWindow = WindowManager.getInstance().getMainWindow();
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, data);
  }
}

export { buildAppMenu as default };
