/**
 * APEX Development Platform - Main IPC Handler
 * Phase 4: UI, Integrations & Analytics
 *
 * Base IPC handler infrastructure with typed channels,
 * error handling, and logging.
 */

import { IpcMain, IpcMainEvent, IpcMainInvokeEvent, BrowserWindow } from 'electron';
import { IPCChannel, IPCChannels } from './index';

/**
 * IPC Response wrapper for consistent API
 */
export interface IPCResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  timestamp: number;
}

/**
 * Create successful IPC response
 */
export function createIPCSuccess<T>(data: T): IPCResponse<T> {
  return {
    success: true,
    data,
    timestamp: Date.now(),
  };
}

/**
 * Create error IPC response
 */
export function createIPCError(
  code: string,
  message: string,
  details?: unknown
): IPCResponse<never> {
  return {
    success: false,
    error: {
      code,
      message,
      details,
    },
    timestamp: Date.now(),
  };
}

/**
 * IPC Handler options
 */
export interface IPCHandlerOptions {
  requiresAuth?: boolean;
  timeout?: number;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

/**
 * Base IPC Handler class
 * Provides consistent handling, logging, and error management
 */
export class IPCHandler {
  private ipcMain: IpcMain;
  private handlers: Map<string, boolean> = new Map();

  constructor(ipcMain: IpcMain) {
    this.ipcMain = ipcMain;
  }

  /**
   * Register an invoke handler (request-response pattern)
   */
  public handle<TParams = unknown, TResult = unknown>(
    channel: IPCChannel,
    handler: (
      event: IpcMainInvokeEvent,
      params: TParams
    ) => Promise<IPCResponse<TResult>>,
    options: IPCHandlerOptions = {}
  ): void {
    if (this.handlers.has(channel)) {
      console.warn(`[IPC] Handler already registered for channel: ${channel}`);
      return;
    }

    this.ipcMain.handle(channel, async (event, params: TParams) => {
      const startTime = Date.now();

      try {
        // Log incoming request
        if (options.logLevel !== 'error') {
          console.log(`[IPC] <- ${channel}`, params);
        }

        // Execute handler
        const result = await handler(event, params);

        // Log response
        const duration = Date.now() - startTime;
        if (options.logLevel !== 'error') {
          console.log(
            `[IPC] -> ${channel} (${duration}ms)`,
            result.success ? 'SUCCESS' : 'ERROR'
          );
        }

        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Unknown error';
        console.error(`[IPC] Error in ${channel}:`, error);

        return createIPCError('HANDLER_ERROR', errorMessage, {
          channel,
          params,
        });
      }
    });

    this.handlers.set(channel, true);
  }

  /**
   * Register a one-way listener (fire-and-forget pattern)
   */
  public on<TParams = unknown>(
    channel: IPCChannel,
    handler: (event: IpcMainEvent, params: TParams) => void
  ): void {
    this.ipcMain.on(channel, (event, params: TParams) => {
      try {
        console.log(`[IPC] <- ${channel} (one-way)`, params);
        handler(event, params);
      } catch (error) {
        console.error(`[IPC] Error in ${channel}:`, error);
      }
    });
  }

  /**
   * Send message to all renderer windows
   */
  public broadcast<T>(channel: IPCChannel, data: T): void {
    const windows = BrowserWindow.getAllWindows();
    windows.forEach((window) => {
      if (!window.isDestroyed()) {
        window.webContents.send(channel, data);
      }
    });
  }

  /**
   * Send message to specific window
   */
  public sendToWindow<T>(
    window: BrowserWindow,
    channel: IPCChannel,
    data: T
  ): void {
    if (!window.isDestroyed()) {
      window.webContents.send(channel, data);
    }
  }

  /**
   * Remove handler
   */
  public removeHandler(channel: IPCChannel): void {
    this.ipcMain.removeHandler(channel);
    this.handlers.delete(channel);
  }

  /**
   * Remove all handlers
   */
  public removeAllHandlers(): void {
    this.handlers.forEach((_, channel) => {
      this.ipcMain.removeHandler(channel);
    });
    this.handlers.clear();
  }

  /**
   * Check if handler is registered
   */
  public hasHandler(channel: IPCChannel): boolean {
    return this.handlers.has(channel);
  }

  /**
   * Get all registered channels
   */
  public getRegisteredChannels(): string[] {
    return Array.from(this.handlers.keys());
  }
}

/**
 * Create a new IPC handler instance
 */
export function createIPCHandler(ipcMain: IpcMain): IPCHandler {
  return new IPCHandler(ipcMain);
}
