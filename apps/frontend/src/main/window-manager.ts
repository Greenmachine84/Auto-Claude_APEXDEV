/**
 * APEX Development Platform - Window Manager
 * Phase 4: UI, Integrations & Analytics
 *
 * Manages BrowserWindow instances for the application.
 * Handles main window, settings window, and other dialogs.
 */

import { BrowserWindow, shell, Notification, nativeTheme } from 'electron';
import * as path from 'path';

/**
 * Window configuration options
 */
export interface WindowConfig {
  width: number;
  height: number;
  minWidth?: number;
  minHeight?: number;
  title: string;
  show?: boolean;
  parent?: BrowserWindow;
  modal?: boolean;
}

/**
 * Default window configuration
 */
const DEFAULT_WINDOW_CONFIG: Partial<WindowConfig> = {
  width: 1400,
  height: 900,
  minWidth: 800,
  minHeight: 600,
  show: false,
};

/**
 * Window Manager
 * Singleton pattern for consistent window management
 */
export class WindowManager {
  private static instance: WindowManager | null = null;
  private mainWindow: BrowserWindow | null = null;
  private settingsWindow: BrowserWindow | null = null;
  private windows: Map<string, BrowserWindow> = new Map();

  private constructor() {}

  /**
   * Get singleton instance
   */
  public static getInstance(): WindowManager {
    if (!WindowManager.instance) {
      WindowManager.instance = new WindowManager();
    }
    return WindowManager.instance;
  }

  /**
   * Create the main application window
   */
  public createMainWindow(): BrowserWindow {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.focus();
      return this.mainWindow;
    }

    this.mainWindow = new BrowserWindow({
      ...DEFAULT_WINDOW_CONFIG,
      width: 1400,
      height: 900,
      title: 'APEX Development Platform',
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        sandbox: true,
        preload: path.join(__dirname, '../preload/index.js'),
      },
    });

    // Load the renderer
    if (process.env['ELECTRON_RENDERER_URL']) {
      this.mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL']);
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(
        path.join(__dirname, '../renderer/index.html')
      );
    }

    // Show when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
    });

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    // Clean up on close
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Handle theme changes
    nativeTheme.on('updated', () => {
      this.mainWindow?.webContents.send(
        'theme:changed',
        nativeTheme.shouldUseDarkColors ? 'dark' : 'light'
      );
    });

    this.windows.set('main', this.mainWindow);
    return this.mainWindow;
  }

  /**
   * Create settings window
   */
  public createSettingsWindow(): BrowserWindow {
    if (this.settingsWindow && !this.settingsWindow.isDestroyed()) {
      this.settingsWindow.focus();
      return this.settingsWindow;
    }

    this.settingsWindow = new BrowserWindow({
      width: 800,
      height: 600,
      minWidth: 600,
      minHeight: 400,
      title: 'Settings',
      parent: this.mainWindow || undefined,
      modal: true,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        sandbox: true,
        preload: path.join(__dirname, '../preload/index.js'),
      },
    });

    // Load settings page
    if (process.env['ELECTRON_RENDERER_URL']) {
      this.settingsWindow.loadURL(process.env['ELECTRON_RENDERER_URL'] + '/#/settings');
    } else {
      this.settingsWindow.loadFile(
        path.join(__dirname, '../renderer/index.html'),
        { hash: '/settings' }
      );
    }

    this.settingsWindow.once('ready-to-show', () => {
      this.settingsWindow?.show();
    });

    this.settingsWindow.on('closed', () => {
      this.settingsWindow = null;
      this.windows.delete('settings');
    });

    this.windows.set('settings', this.settingsWindow);
    return this.settingsWindow;
  }

  /**
   * Get the main window instance
   */
  public getMainWindow(): BrowserWindow | null {
    return this.mainWindow;
  }

  /**
   * Get window by name
   */
  public getWindow(name: string): BrowserWindow | undefined {
    return this.windows.get(name);
  }

  /**
   * Close all windows
   */
  public closeAllWindows(): void {
    this.windows.forEach((window) => {
      if (!window.isDestroyed()) {
        window.close();
      }
    });
    this.windows.clear();
    this.mainWindow = null;
    this.settingsWindow = null;
  }

  /**
   * Set window title
   */
  public setWindowTitle(title: string): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.setTitle(`${title} - APEX Development Platform`);
    }
  }

  /**
   * Show native notification
   */
  public showNotification(title: string, body: string): void {
    if (Notification.isSupported()) {
      const notification = new Notification({
        title,
        body,
        icon: path.join(__dirname, '../../assets/icon.png'),
      });
      notification.show();
    }
  }

  /**
   * Toggle dev tools for main window
   */
  public toggleDevTools(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.toggleDevTools();
    }
  }

  /**
   * Reload main window
   */
  public reloadMainWindow(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.reload();
    }
  }

  /**
   * Focus main window
   */
  public focusMainWindow(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      if (this.mainWindow.isMinimized()) {
        this.mainWindow.restore();
      }
      this.mainWindow.focus();
    }
  }

  /**
   * Minimize main window
   */
  public minimizeMainWindow(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.minimize();
    }
  }

  /**
   * Maximize/restore main window
   */
  public toggleMaximize(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      if (this.mainWindow.isMaximized()) {
        this.mainWindow.unmaximize();
      } else {
        this.mainWindow.maximize();
      }
    }
  }

  /**
   * Reset for testing
   */
  public static resetInstance(): void {
    WindowManager.instance = null;
  }
}
