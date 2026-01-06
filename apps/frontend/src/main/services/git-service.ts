/**
 * APEX Development Platform - Git Service
 * Phase 4: UI, Integrations & Analytics
 *
 * Provides Git operations for the UI layer.
 * Wraps git commands with typed interfaces.
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execAsync = promisify(exec);

/** Git status file entry */
export interface GitStatusEntry {
  status: 'M' | 'A' | 'D' | 'R' | 'C' | 'U' | '?';
  staged: boolean;
  path: string;
  originalPath?: string;
}

/** Git branch info */
export interface GitBranch {
  name: string;
  current: boolean;
  remote?: string;
  upstream?: string;
  ahead: number;
  behind: number;
}

/** Git commit info */
export interface GitCommit {
  hash: string;
  shortHash: string;
  author: string;
  email: string;
  date: string;
  message: string;
  body?: string;
}

/** Git diff info */
export interface GitDiff {
  path: string;
  additions: number;
  deletions: number;
  hunks: GitDiffHunk[];
}

/** Git diff hunk */
export interface GitDiffHunk {
  header: string;
  startLine: number;
  lineCount: number;
  content: string;
}

/**
 * Git Service
 * Provides Git operations for workspace management
 */
export class GitService {
  private static instance: GitService | null = null;
  private workingDir: string | null = null;

  private constructor() {}

  public static getInstance(): GitService {
    if (!GitService.instance) {
      GitService.instance = new GitService();
    }
    return GitService.instance;
  }

  /**
   * Set working directory for git operations
   */
  public setWorkingDirectory(dir: string): void {
    this.workingDir = dir;
  }

  /**
   * Get current working directory
   */
  public getWorkingDirectory(): string | null {
    return this.workingDir;
  }

  /**
   * Execute git command
   */
  private async git(args: string, cwd?: string): Promise<string> {
    const workDir = cwd || this.workingDir;
    if (!workDir) throw new Error('Working directory not set');

    try {
      const { stdout } = await execAsync(`git ${args}`, {
        cwd: workDir,
        maxBuffer: 10 * 1024 * 1024, // 10MB
      });
      return stdout.trim();
    } catch (error) {
      const err = error as { stderr?: string; message: string };
      throw new Error(err.stderr || err.message);
    }
  }

  /**
   * Check if directory is a git repository
   */
  public async isRepository(dir?: string): Promise<boolean> {
    try {
      await this.git('rev-parse --is-inside-work-tree', dir);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get repository status
   */
  public async getStatus(): Promise<GitStatusEntry[]> {
    const output = await this.git('status --porcelain=v1');
    if (!output) return [];

    return output.split('\n').map((line) => {
      const indexStatus = line[0];
      const workTreeStatus = line[1];
      const filePath = line.substring(3);

      let status: GitStatusEntry['status'];
      let staged = false;

      if (indexStatus !== ' ' && indexStatus !== '?') {
        status = indexStatus as GitStatusEntry['status'];
        staged = true;
      } else {
        status = (workTreeStatus === '?' ? '?' : workTreeStatus) as GitStatusEntry['status'];
      }

      return { status, staged, path: filePath };
    });
  }

  /**
   * Get current branch
   */
  public async getCurrentBranch(): Promise<string> {
    return this.git('branch --show-current');
  }

  /**
   * Get all branches
   */
  public async getBranches(): Promise<GitBranch[]> {
    const output = await this.git('branch -a --format="%(refname:short)|%(HEAD)|%(upstream:short)|%(upstream:track)"');
    if (!output) return [];

    return output.split('\n').map((line) => {
      const [name, head, upstream, track] = line.split('|');
      const aheadMatch = track?.match(/ahead (\d+)/);
      const behindMatch = track?.match(/behind (\d+)/);

      return {
        name,
        current: head === '*',
        upstream: upstream || undefined,
        remote: name.startsWith('origin/') ? 'origin' : undefined,
        ahead: aheadMatch ? parseInt(aheadMatch[1], 10) : 0,
        behind: behindMatch ? parseInt(behindMatch[1], 10) : 0,
      };
    });
  }

  /**
   * Get recent commits
   */
  public async getCommits(count = 50): Promise<GitCommit[]> {
    const format = '%H|%h|%an|%ae|%aI|%s';
    const output = await this.git(`log -${count} --format="${format}"`);
    if (!output) return [];

    return output.split('\n').map((line) => {
      const [hash, shortHash, author, email, date, message] = line.split('|');
      return { hash, shortHash, author, email, date, message };
    });
  }

  /**
   * Get diff for file
   */
  public async getDiff(filePath?: string, staged = false): Promise<string> {
    const stageFlag = staged ? '--cached' : '';
    const pathSpec = filePath ? `-- "${filePath}"` : '';
    return this.git(`diff ${stageFlag} ${pathSpec}`);
  }

  /**
   * Stage file(s)
   */
  public async stage(files: string | string[]): Promise<void> {
    const paths = Array.isArray(files) ? files.join('" "') : files;
    await this.git(`add "${paths}"`);
  }

  /**
   * Unstage file(s)
   */
  public async unstage(files: string | string[]): Promise<void> {
    const paths = Array.isArray(files) ? files.join('" "') : files;
    await this.git(`reset HEAD "${paths}"`);
  }

  /**
   * Commit staged changes
   */
  public async commit(message: string): Promise<string> {
    const escapedMessage = message.replace(/"/g, '\\"');
    return this.git(`commit -m "${escapedMessage}"`);
  }

  /**
   * Checkout branch
   */
  public async checkout(branch: string, create = false): Promise<void> {
    const flag = create ? '-b' : '';
    await this.git(`checkout ${flag} ${branch}`);
  }

  /**
   * Pull from remote
   */
  public async pull(remote = 'origin', branch?: string): Promise<string> {
    const branchArg = branch || '';
    return this.git(`pull ${remote} ${branchArg}`);
  }

  /**
   * Push to remote
   */
  public async push(remote = 'origin', branch?: string, force = false): Promise<string> {
    const branchArg = branch || '';
    const forceFlag = force ? '--force' : '';
    return this.git(`push ${forceFlag} ${remote} ${branchArg}`);
  }

  /**
   * Fetch from remote
   */
  public async fetch(remote = 'origin', prune = true): Promise<void> {
    const pruneFlag = prune ? '--prune' : '';
    await this.git(`fetch ${remote} ${pruneFlag}`);
  }

  /**
   * Get remote URL
   */
  public async getRemoteUrl(remote = 'origin'): Promise<string | null> {
    try {
      return await this.git(`remote get-url ${remote}`);
    } catch {
      return null;
    }
  }

  public static resetInstance(): void {
    GitService.instance = null;
  }
}
