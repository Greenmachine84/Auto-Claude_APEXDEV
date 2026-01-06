/**
 * APEX Development Platform - Terminal Service
 * Phase 4: UI, Integrations & Analytics
 *
 * Manages terminal sessions for the UI.
 * Handles PTY creation, I/O, and lifecycle.
 */

import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import { EventEmitter } from 'events';
import * as os from 'os';

/** Terminal session */
export interface TerminalSession {
  id: string;
  pid: number;
  cwd: string;
  shell: string;
  title: string;
  createdAt: Date;
  isActive: boolean;
}

/** Terminal output event */
export interface TerminalOutput {
  sessionId: string;
  data: string;
  timestamp: Date;
}

/**
 * Terminal Service
 * Manages multiple terminal sessions
 */
export class TerminalService extends EventEmitter {
  private static instance: TerminalService | null = null;
  private sessions: Map<string, TerminalSession> = new Map();
  private processes: Map<string, ChildProcessWithoutNullStreams> = new Map();
  private sessionIdCounter = 0;

  private constructor() {
    super();
  }

  public static getInstance(): TerminalService {
    if (!TerminalService.instance) {
      TerminalService.instance = new TerminalService();
    }
    return TerminalService.instance;
  }

  /**
   * Create new terminal session
   */
  public createSession(cwd?: string, shell?: string): TerminalSession {
    const id = `term_${++this.sessionIdCounter}`;
    const defaultShell = this.getDefaultShell();
    const sessionShell = shell || defaultShell;
    const sessionCwd = cwd || os.homedir();

    const proc = spawn(sessionShell, [], {
      cwd: sessionCwd,
      env: { ...process.env, TERM: 'xterm-256color' },
      shell: true,
    });

    const session: TerminalSession = {
      id,
      pid: proc.pid || 0,
      cwd: sessionCwd,
      shell: sessionShell,
      title: `Terminal ${this.sessionIdCounter}`,
      createdAt: new Date(),
      isActive: true,
    };

    // Handle output
    proc.stdout.on('data', (data: Buffer) => {
      const output: TerminalOutput = {
        sessionId: id,
        data: data.toString(),
        timestamp: new Date(),
      };
      this.emit('output', output);
    });

    proc.stderr.on('data', (data: Buffer) => {
      const output: TerminalOutput = {
        sessionId: id,
        data: data.toString(),
        timestamp: new Date(),
      };
      this.emit('output', output);
    });

    proc.on('exit', (code) => {
      session.isActive = false;
      this.emit('exit', { sessionId: id, code });
    });

    proc.on('error', (error) => {
      this.emit('error', { sessionId: id, error });
    });

    this.sessions.set(id, session);
    this.processes.set(id, proc);
    this.emit('created', session);

    return session;
  }

  /**
   * Write to terminal session
   */
  public write(sessionId: string, data: string): boolean {
    const proc = this.processes.get(sessionId);
    if (!proc || !proc.stdin) return false;

    proc.stdin.write(data);
    return true;
  }

  /**
   * Resize terminal
   */
  public resize(sessionId: string, cols: number, rows: number): boolean {
    const proc = this.processes.get(sessionId);
    if (!proc) return false;

    // Note: For full PTY support, use node-pty instead
    // This is a simplified implementation
    this.emit('resize', { sessionId, cols, rows });
    return true;
  }

  /**
   * Kill terminal session
   */
  public kill(sessionId: string): boolean {
    const proc = this.processes.get(sessionId);
    const session = this.sessions.get(sessionId);

    if (!proc || !session) return false;

    proc.kill('SIGTERM');
    session.isActive = false;

    // Force kill after timeout
    setTimeout(() => {
      if (!proc.killed) proc.kill('SIGKILL');
    }, 1000);

    return true;
  }

  /**
   * Get session by ID
   */
  public getSession(sessionId: string): TerminalSession | undefined {
    return this.sessions.get(sessionId);
  }

  /**
   * Get all sessions
   */
  public getAllSessions(): TerminalSession[] {
    return Array.from(this.sessions.values());
  }

  /**
   * Get active sessions
   */
  public getActiveSessions(): TerminalSession[] {
    return Array.from(this.sessions.values()).filter((s) => s.isActive);
  }

  /**
   * Destroy session
   */
  public destroySession(sessionId: string): void {
    this.kill(sessionId);
    this.processes.delete(sessionId);
    this.sessions.delete(sessionId);
    this.emit('destroyed', { sessionId });
  }

  /**
   * Destroy all sessions
   */
  public destroyAllSessions(): void {
    const sessionIds = Array.from(this.sessions.keys());
    sessionIds.forEach((id) => this.destroySession(id));
  }

  /**
   * Get default shell for platform
   */
  private getDefaultShell(): string {
    if (process.platform === 'win32') {
      return process.env.COMSPEC || 'cmd.exe';
    }
    return process.env.SHELL || '/bin/bash';
  }

  /**
   * Set session title
   */
  public setTitle(sessionId: string, title: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.title = title;
      this.emit('titleChanged', { sessionId, title });
    }
  }

  public static resetInstance(): void {
    TerminalService.instance = null;
  }
}
