/**
 * APEX Development Platform - Backend Service
 * Phase 4: UI, Integrations & Analytics
 *
 * Manages communication with Python backend process.
 * Handles process spawning, JSON-RPC communication, and lifecycle.
 */

import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import { app } from 'electron';
import { EventEmitter } from 'events';

/** Backend request */
export interface BackendRequest {
  id: string;
  method: string;
  params: unknown;
}

/** Backend response */
export interface BackendResponse<T = unknown> {
  id: string;
  result?: T;
  error?: { code: number; message: string; data?: unknown };
}

/** Pending request tracker */
interface PendingRequest {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
  timeout: NodeJS.Timeout;
}

/**
 * Backend Service
 * Singleton for Python backend communication
 */
export class BackendService extends EventEmitter {
  private static instance: BackendService | null = null;
  private process: ChildProcess | null = null;
  private pendingRequests: Map<string, PendingRequest> = new Map();
  private requestId = 0;
  private buffer = '';
  private isStarting = false;
  private isConnected = false;
  private readonly requestTimeout = 30000; // 30 seconds

  private constructor() {
    super();
  }

  public static getInstance(): BackendService {
    if (!BackendService.instance) {
      BackendService.instance = new BackendService();
    }
    return BackendService.instance;
  }

  /**
   * Start the backend process
   */
  public async start(): Promise<void> {
    if (this.isConnected || this.isStarting) return;
    this.isStarting = true;

    try {
      const pythonPath = this.getPythonPath();
      const backendPath = this.getBackendPath();

      console.log('[Backend] Starting process...', { pythonPath, backendPath });

      this.process = spawn(pythonPath, ['-m', 'apex_backend'], {
        cwd: backendPath,
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      this.setupProcessHandlers();
      await this.waitForReady();

      this.isConnected = true;
      this.isStarting = false;
      this.emit('connected');
      console.log('[Backend] Connected successfully');
    } catch (error) {
      this.isStarting = false;
      console.warn('[Backend] Backend unavailable (app continues without it):', error);
      this.emit('backend-unavailable');
      // Don't throw - app works without backend
    }
  }

  /**
   * Stop the backend process
   */
  public async stop(): Promise<void> {
    if (!this.process) return;

    console.log('[Backend] Stopping process...');

    // Clear pending requests
    this.pendingRequests.forEach(({ reject, timeout }) => {
      clearTimeout(timeout);
      reject(new Error('Backend shutting down'));
    });
    this.pendingRequests.clear();

    // Graceful shutdown
    try {
      await this.request('shutdown', {}, 5000);
    } catch {
      // Ignore shutdown errors
    }

    // Force kill if needed
    if (this.process && !this.process.killed) {
      this.process.kill('SIGTERM');
      await new Promise((resolve) => setTimeout(resolve, 1000));
      if (this.process && !this.process.killed) {
        this.process.kill('SIGKILL');
      }
    }

    this.process = null;
    this.isConnected = false;
    this.emit('disconnected');
    console.log('[Backend] Stopped');
  }

  /**
   * Send request to backend
   */
  public async request<T>(
    method: string,
    params: unknown = {},
    timeout = this.requestTimeout
  ): Promise<T> {
    if (!this.isConnected || !this.process) {
      throw new Error('Backend not connected');
    }

    const id = `req_${++this.requestId}`;
    const request: BackendRequest = { id, method, params };

    return new Promise((resolve, reject) => {
      const timeoutHandle = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, timeout);

      this.pendingRequests.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
        timeout: timeoutHandle,
      });

      const message = JSON.stringify(request) + '\n';
      this.process!.stdin?.write(message);
    });
  }

  /**
   * Check if connected
   */
  public isActive(): boolean {
    return this.isConnected;
  }

  private setupProcessHandlers(): void {
    if (!this.process) return;

    this.process.stdout?.on('data', (data: Buffer) => {
      this.buffer += data.toString();
      this.processBuffer();
    });

    this.process.stderr?.on('data', (data: Buffer) => {
      console.error('[Backend] stderr:', data.toString());
    });

    this.process.on('error', (error) => {
      console.warn('[Backend] Process error (non-fatal):', error.message);
      this.isConnected = false;
      this.emit('backend-unavailable');
    });

    this.process.on('exit', (code) => {
      console.log(`[Backend] Process exited with code ${code}`);
      this.isConnected = false;
      this.emit('disconnected');
    });
  }

  private processBuffer(): void {
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const response: BackendResponse = JSON.parse(line);
        this.handleResponse(response);
      } catch (error) {
        console.error('[Backend] Failed to parse response:', line);
      }
    }
  }

  private handleResponse(response: BackendResponse): void {
    const pending = this.pendingRequests.get(response.id);
    if (!pending) {
      console.warn('[Backend] Unknown response ID:', response.id);
      return;
    }

    clearTimeout(pending.timeout);
    this.pendingRequests.delete(response.id);

    if (response.error) {
      pending.reject(new Error(response.error.message));
    } else {
      pending.resolve(response.result);
    }
  }

  private async waitForReady(timeout = 10000): Promise<void> {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      try {
        await new Promise((resolve) => setTimeout(resolve, 100));
        // Check if process is running
        if (this.process && !this.process.killed) {
          return;
        }
      } catch {
        // Continue waiting
      }
    }
    throw new Error('Backend failed to start within timeout');
  }

  private getPythonPath(): string {
    return process.env.PYTHON_PATH || 'python';
  }

  private getBackendPath(): string {
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      return path.join(__dirname, '../../../../backend');
    }
    return path.join(app.getAppPath(), 'backend');
  }

  public static resetInstance(): void {
    BackendService.instance = null;
  }
}



