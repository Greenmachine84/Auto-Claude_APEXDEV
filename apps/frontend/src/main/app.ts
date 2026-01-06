/**
 * APEX Development Platform - App Lifecycle
 * Phase 4: UI, Integrations & Analytics
 *
 * Manages application lifecycle events including startup,
 * shutdown, and state persistence.
 */

import { app, BrowserWindow, dialog } from 'electron';
import * as path from 'path';
import * as fs from 'fs/promises';
import { BackendService } from './services/backend-service';

/**
 * Application state persisted between sessions
 */
export interface AppState {
  windowBounds: {
    x?: number;
    y?: number;
    width: number;
    height: number;
    isMaximized: boolean;
  };
  lastOpenedProject?: string;
  recentProjects: string[];
  theme: 'light' | 'dark' | 'system';
}

/**
 * Default application state
 */
const DEFAULT_STATE: AppState = {
  windowBounds: {
    width: 1400,
    height: 900,
    isMaximized: false,
  },
  recentProjects: [],
  theme: 'system',
};

/**
 * Application lifecycle manager
 * Singleton pattern for consistent state management
 */
export class AppLifecycle {
  private static instance: AppLifecycle | null = null;
  private state: AppState;
  private statePath: string;
  private isShuttingDown = false;
  private mainWindow: BrowserWindow | null = null;

  private constructor() {
    this.statePath = path.join(app.getPath('userData'), 'app-state.json');
    this.state = { ...DEFAULT_STATE };
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): AppLifecycle {
    if (!AppLifecycle.instance) {
      AppLifecycle.instance = new AppLifecycle();
    }
    return AppLifecycle.instance;
  }

  /**
   * Load application state from disk
   */
  public async loadState(): Promise<AppState> {
    try {
      const data = await fs.readFile(this.statePath, 'utf-8');
      this.state = { ...DEFAULT_STATE, ...JSON.parse(data) };
      console.log('[App] State loaded successfully');
    } catch (error) {
      console.log('[App] No saved state found, using defaults');
      this.state = { ...DEFAULT_STATE };
    }
    return this.state;
  }

  /**
   * Save application state to disk
   */
  public async saveState(): Promise<void> {
    try {
      // Update window bounds from current window
      if (this.mainWindow && !this.mainWindow.isDestroyed()) {
        const bounds = this.mainWindow.getBounds();
        this.state.windowBounds = {
          x: bounds.x,
          y: bounds.y,
          width: bounds.width,
          height: bounds.height,
          isMaximized: this.mainWindow.isMaximized(),
        };
      }

      await fs.writeFile(
        this.statePath,
        JSON.stringify(this.state, null, 2),
        'utf-8'
      );
      console.log('[App] State saved successfully');
    } catch (error) {
      console.error('[App] Failed to save state:', error);
    }
  }

  /**
   * Called when main window is created
   */
  public async onWindowCreated(window: BrowserWindow): Promise<void> {
    this.mainWindow = window;
    await this.loadState();

    // Apply saved window bounds
    const { windowBounds } = this.state;
    if (windowBounds.x !== undefined && windowBounds.y !== undefined) {
      window.setBounds({
        x: windowBounds.x,
        y: windowBounds.y,
        width: windowBounds.width,
        height: windowBounds.height,
      });
    }

    if (windowBounds.isMaximized) {
      window.maximize();
    }

    // Save state periodically
    setInterval(() => this.saveState(), 30000);
  }

  /**
   * Get current application state
   */
  public getState(): AppState {
    return { ...this.state };
  }

  /**
   * Update application state
   */
  public updateState(updates: Partial<AppState>): void {
    this.state = { ...this.state, ...updates };
  }

  /**
   * Add project to recent projects list
   */
  public addRecentProject(projectPath: string): void {
    const recent = this.state.recentProjects.filter((p) => p !== projectPath);
    recent.unshift(projectPath);
    this.state.recentProjects = recent.slice(0, 10); // Keep last 10
    this.state.lastOpenedProject = projectPath;
  }

  /**
   * Graceful application shutdown
   */
  public async shutdown(): Promise<void> {
    if (this.isShuttingDown) {
      return;
    }
    this.isShuttingDown = true;

    console.log('[App] Initiating graceful shutdown...');

    try {
      // Save application state
      await this.saveState();

      // Stop backend service
      const backendService = BackendService.getInstance();
      await backendService.stop();

      console.log('[App] Shutdown complete');
    } catch (error) {
      console.error('[App] Error during shutdown:', error);
    }
  }

  /**
   * Show error dialog to user
   */
  public showError(title: string, message: string): void {
    dialog.showErrorBox(title, message);
  }

  /**
   * Show confirmation dialog
   */
  public async showConfirmation(
    title: string,
    message: string
  ): Promise<boolean> {
    const result = await dialog.showMessageBox({
      type: 'question',
      buttons: ['Yes', 'No'],
      defaultId: 1,
      title,
      message,
    });
    return result.response === 0;
  }

  /**
   * Reset for testing
   */
  public static resetInstance(): void {
    AppLifecycle.instance = null;
  }
}
