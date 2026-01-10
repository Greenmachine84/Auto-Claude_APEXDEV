/**
 * Virtual GitHub Repository IPC handlers
 * Enables working with GitHub repos via API without local clone
 */

import { ipcMain } from 'electron';
import { IPC_CHANNELS } from '../../../shared/constants';
import type { IPCResult, VirtualRepoInfo } from '../../../shared/types';
import { projectStore } from '../../project-store';

interface GitHubFileInfo {
  name: string;
  path: string;
  sha: string;
  size: number;
  type: 'file' | 'dir' | 'symlink' | 'submodule';
  download_url?: string;
  html_url?: string;
}

interface GitHubFileContent {
  name: string;
  path: string;
  sha: string;
  size: number;
  content?: string;
  encoding?: string;
  download_url?: string;
}

interface GitHubTreeItem {
  path: string;
  mode: string;
  type: 'blob' | 'tree';
  sha: string;
  size?: number;
}

interface GitHubTree {
  sha: string;
  tree: GitHubTreeItem[];
  truncated: boolean;
}

/**
 * Make authenticated GitHub API request
 */
async function githubApiFetch<T>(
  token: string,
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = endpoint.startsWith('https://') 
    ? endpoint 
    : `https://api.github.com${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/vnd.github.v3+json',
      Authorization: `Bearer ${token}`,
      'User-Agent': 'APEXDEV-App',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `GitHub API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get project by ID and validate it has virtual repo info
 */
function getVirtualProject(projectId: string): { project: any; virtualRepo: VirtualRepoInfo; token: string } | null {
  const project = projectStore.getProject(projectId);
  if (!project) return null;
  if (!project.virtualRepo || !project.githubToken) return null;
  return {
    project,
    virtualRepo: project.virtualRepo,
    token: project.githubToken
  };
}

/**
 * List files in a directory of a virtual GitHub repo
 */
export function registerVirtualListFiles(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VIRTUAL_LIST_FILES,
    async (
      _,
      projectId: string,
      path: string = ''
    ): Promise<IPCResult<GitHubFileInfo[]>> => {
      try {
        const vp = getVirtualProject(projectId);
        if (!vp) {
          return { success: false, error: 'Project not found or not a virtual project' };
        }

        const { virtualRepo, token } = vp;
        const ref = virtualRepo.defaultBranch || 'main';
        const endpoint = `/repos/${virtualRepo.fullName}/contents/${path}?ref=${ref}`;
        
        const files = await githubApiFetch<GitHubFileInfo[]>(token, endpoint);
        
        return { success: true, data: files };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to list files'
        };
      }
    }
  );
}

/**
 * Get file content from a virtual GitHub repo
 */
export function registerVirtualGetFile(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VIRTUAL_GET_FILE,
    async (
      _,
      projectId: string,
      path: string
    ): Promise<IPCResult<{ content: string; sha: string; encoding: string }>> => {
      try {
        const vp = getVirtualProject(projectId);
        if (!vp) {
          return { success: false, error: 'Project not found or not a virtual project' };
        }

        const { virtualRepo, token } = vp;
        const ref = virtualRepo.defaultBranch || 'main';
        const endpoint = `/repos/${virtualRepo.fullName}/contents/${path}?ref=${ref}`;
        
        const file = await githubApiFetch<GitHubFileContent>(token, endpoint);
        
        // Decode base64 content
        let content = '';
        if (file.content && file.encoding === 'base64') {
          content = Buffer.from(file.content, 'base64').toString('utf-8');
        }
        
        return { 
          success: true, 
          data: { 
            content, 
            sha: file.sha,
            encoding: file.encoding || 'utf-8'
          } 
        };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to get file'
        };
      }
    }
  );
}

/**
 * Create a new file in a virtual GitHub repo
 */
export function registerVirtualCreateFile(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VIRTUAL_CREATE_FILE,
    async (
      _,
      projectId: string,
      path: string,
      content: string,
      message: string
    ): Promise<IPCResult<{ sha: string }>> => {
      try {
        const vp = getVirtualProject(projectId);
        if (!vp) {
          return { success: false, error: 'Project not found or not a virtual project' };
        }

        const { virtualRepo, token } = vp;
        const branch = virtualRepo.defaultBranch || 'main';
        const endpoint = `/repos/${virtualRepo.fullName}/contents/${path}`;
        
        const result = await githubApiFetch<{ content: { sha: string } }>(token, endpoint, {
          method: 'PUT',
          body: JSON.stringify({
            message: message || `Create ${path}`,
            content: Buffer.from(content).toString('base64'),
            branch
          })
        });
        
        return { success: true, data: { sha: result.content.sha } };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to create file'
        };
      }
    }
  );
}

/**
 * Update an existing file in a virtual GitHub repo
 */
export function registerVirtualUpdateFile(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VIRTUAL_UPDATE_FILE,
    async (
      _,
      projectId: string,
      path: string,
      content: string,
      sha: string,
      message: string
    ): Promise<IPCResult<{ sha: string }>> => {
      try {
        const vp = getVirtualProject(projectId);
        if (!vp) {
          return { success: false, error: 'Project not found or not a virtual project' };
        }

        const { virtualRepo, token } = vp;
        const branch = virtualRepo.defaultBranch || 'main';
        const endpoint = `/repos/${virtualRepo.fullName}/contents/${path}`;
        
        const result = await githubApiFetch<{ content: { sha: string } }>(token, endpoint, {
          method: 'PUT',
          body: JSON.stringify({
            message: message || `Update ${path}`,
            content: Buffer.from(content).toString('base64'),
            sha,
            branch
          })
        });
        
        return { success: true, data: { sha: result.content.sha } };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to update file'
        };
      }
    }
  );
}

/**
 * Delete a file from a virtual GitHub repo
 */
export function registerVirtualDeleteFile(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VIRTUAL_DELETE_FILE,
    async (
      _,
      projectId: string,
      path: string,
      sha: string,
      message: string
    ): Promise<IPCResult<void>> => {
      try {
        const vp = getVirtualProject(projectId);
        if (!vp) {
          return { success: false, error: 'Project not found or not a virtual project' };
        }

        const { virtualRepo, token } = vp;
        const branch = virtualRepo.defaultBranch || 'main';
        const endpoint = `/repos/${virtualRepo.fullName}/contents/${path}`;
        
        await githubApiFetch(token, endpoint, {
          method: 'DELETE',
          body: JSON.stringify({
            message: message || `Delete ${path}`,
            sha,
            branch
          })
        });
        
        return { success: true };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to delete file'
        };
      }
    }
  );
}

/**
 * Get the full repository tree (recursive)
 */
export function registerVirtualGetTree(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VIRTUAL_GET_TREE,
    async (
      _,
      projectId: string
    ): Promise<IPCResult<GitHubTreeItem[]>> => {
      try {
        const vp = getVirtualProject(projectId);
        if (!vp) {
          return { success: false, error: 'Project not found or not a virtual project' };
        }

        const { virtualRepo, token } = vp;
        const ref = virtualRepo.defaultBranch || 'main';
        const endpoint = `/repos/${virtualRepo.fullName}/git/trees/${ref}?recursive=1`;
        
        const tree = await githubApiFetch<GitHubTree>(token, endpoint);
        
        return { success: true, data: tree.tree };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to get tree'
        };
      }
    }
  );
}


/**
 * Validate a GitHub PAT token
 */
export function registerValidatePat(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_VALIDATE_PAT,
    async (
      _,
      token: string
    ): Promise<IPCResult<{ login: string; name: string; avatar_url: string }>> => {
      try {
        if (!token || !token.trim()) {
          return { success: false, error: 'Token is required' };
        }

        const user = await githubApiFetch<{ login: string; name: string; avatar_url: string }>(token, '/user');
        return { success: true, data: user };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Invalid token'
        };
      }
    }
  );
}

/**
 * List repositories using a PAT token
 */
export function registerListReposWithPat(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_LIST_REPOS_WITH_PAT,
    async (
      _,
      token: string
    ): Promise<IPCResult<Array<{
      id: number;
      name: string;
      full_name: string;
      description: string | null;
      private: boolean;
      default_branch: string;
      clone_url: string;
      html_url: string;
      updated_at: string;
    }>>> => {
      try {
        if (!token || !token.trim()) {
          return { success: false, error: 'Token is required' };
        }

        const repos = await githubApiFetch<Array<{
          id: number;
          name: string;
          full_name: string;
          description: string | null;
          private: boolean;
          default_branch: string;
          clone_url: string;
          html_url: string;
          updated_at: string;
        }>>(token, '/user/repos?per_page=100&sort=updated');

        return { success: true, data: repos };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to list repositories'
        };
      }
    }
  );
}

/**
 * Get a specific repository using a PAT token
 */
export function registerGetRepoWithPat(): void {
  ipcMain.handle(
    IPC_CHANNELS.GITHUB_GET_REPO_WITH_PAT,
    async (
      _,
      { token, owner, repo }: { token: string; owner: string; repo: string }
    ): Promise<IPCResult<{
      id: number;
      name: string;
      full_name: string;
      description: string | null;
      private: boolean;
      default_branch: string;
      clone_url: string;
      html_url: string;
      updated_at: string;
    }>> => {
      try {
        if (!token || !token.trim()) {
          return { success: false, error: 'Token is required' };
        }

        const repoData = await githubApiFetch<{
          id: number;
          name: string;
          full_name: string;
          description: string | null;
          private: boolean;
          default_branch: string;
          clone_url: string;
          html_url: string;
          updated_at: string;
        }>(token, `/repos/${owner}/${repo}`);

        return { success: true, data: repoData };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to get repository'
        };
      }
    }
  );
}

/**
 * Register all virtual repo handlers
 */
export function registerVirtualRepoHandlers(): void {
  console.log('[GitHub Virtual] Registering virtual repo handlers');
  registerVirtualListFiles();
  registerVirtualGetFile();
  registerVirtualCreateFile();
  registerVirtualUpdateFile();
  registerVirtualDeleteFile();
  registerVirtualGetTree();
  registerValidatePat();
  registerListReposWithPat();
  registerGetRepoWithPat();
  console.log('[GitHub Virtual] Virtual repo handlers registered');
}
