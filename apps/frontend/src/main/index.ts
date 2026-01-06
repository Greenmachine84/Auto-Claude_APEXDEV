/**
 * APEX Development Platform - Main Entry Point
 * Phase 4: UI, Integrations & Analytics
 *
 * Application entry point for Electron main process.
 * Handles app initialization, window creation, and backend spawn.
 */

import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { AppLifecycle } from './app';
import { WindowManager } from './window-manager';
import { registerAllIPCHandlers } from './ipc';
import { BackendService } from './services/backend-service';

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  // Handle second instance
  app.on('second-instance', () => {
    const mainWindow = WindowManager.getInstance().getMainWindow();
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  // Initialize application
  initializeApp();
}

/**
 * Main application initialization
 */
async function initializeApp(): Promise<void> {
  const lifecycle = AppLifecycle.getInstance();
  const windowManager = WindowManager.getInstance();
  const backendService = BackendService.getInstance();

  // Register IPC handlers before window creation
  registerAllIPCHandlers(ipcMain);

  // App ready handler
  app.whenReady().then(async () => {
    console.log('[Main] Application ready');

    // Start backend service
    try {
      await backendService.start();
      console.log('[Main] Backend service started');
    } catch (error) {
      console.error('[Main] Failed to start backend:', error);
    }

    // Create main window
    const mainWindow = windowManager.createMainWindow();
    await lifecycle.onWindowCreated(mainWindow);

    // macOS: Re-create window when dock icon clicked
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        windowManager.createMainWindow();
      }
    });
  });

  // Quit when all windows are closed (except macOS)
  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      lifecycle.shutdown();
    }
  });

  // Graceful shutdown
  app.on('before-quit', async (event) => {
    event.preventDefault();
    await lifecycle.shutdown();
    app.exit(0);
  });

  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    console.error('[Main] Uncaught exception:', error);
  });

  process.on('unhandledRejection', (reason) => {
    console.error('[Main] Unhandled rejection:', reason);
  });
}

// Export for testing
export { initializeApp };
