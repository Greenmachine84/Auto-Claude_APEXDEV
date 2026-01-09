import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Github, Search, Loader2, Lock, Globe, GitBranch, AlertCircle, CheckCircle2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import type { VirtualRepoInfo } from '../../shared/types';

interface ConnectGitHubRepoModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConnect: (repoInfo: VirtualRepoInfo, token: string) => void;
}

interface RepoListItem {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  private: boolean;
  default_branch: string;
  clone_url: string;
  html_url: string;
  updated_at: string;
}

export function ConnectGitHubRepoModal({
  open,
  onOpenChange,
  onConnect,
}: ConnectGitHubRepoModalProps) {
  const { t } = useTranslation(['github', 'common']);
  const [activeTab, setActiveTab] = useState<'browse' | 'url'>('browse');
  const [token, setToken] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [repos, setRepos] = useState<RepoListItem[]>([]);
  const [isLoadingRepos, setIsLoadingRepos] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [selectedRepo, setSelectedRepo] = useState<RepoListItem | null>(null);

  // Filter repos by search query
  const filteredRepos = repos.filter(repo =>
    repo.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (repo.description?.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Validate token and fetch repos via IPC (main process handles API calls)
  const validateAndFetchRepos = async () => {
    if (!token.trim()) {
      setError('Please enter a GitHub Personal Access Token');
      return;
    }

    setIsValidating(true);
    setError(null);

    try {
      // Validate token via IPC
      const validateResult = await window.electronAPI.github.validatePat(token);

      if (!validateResult.success) {
        throw new Error(validateResult.error || 'Invalid token or token lacks required permissions');
      }

      setIsAuthenticated(true);
      setIsLoadingRepos(true);

      // Fetch repos via IPC
      const reposResult = await window.electronAPI.github.listReposWithPat(token);

      if (reposResult.success && reposResult.data) {
        setRepos(reposResult.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to authenticate');
      setIsAuthenticated(false);
    } finally {
      setIsValidating(false);
      setIsLoadingRepos(false);
    }
  };

  // Fetch repo from URL via IPC
  const fetchRepoFromUrl = async () => {
    if (!token.trim()) {
      setError('Please enter a GitHub Personal Access Token first');
      return;
    }

    // Parse GitHub URL
    const urlPattern = /github\.com[/:]([^/]+)\/([^/\s.]+)/;
    const match = repoUrl.match(urlPattern);

    if (!match) {
      setError('Invalid GitHub URL. Use format: https://github.com/owner/repo');
      return;
    }

    const [, owner, repo] = match;
    const repoName = repo.replace(/\.git$/, '');

    setIsValidating(true);
    setError(null);

    try {
      const result = await window.electronAPI.github.getRepoWithPat(token, owner, repoName);

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch repository');
      }

      const repoData = result.data!;

      // Connect directly
      handleConnect({
        id: repoData.id,
        name: repoData.name,
        full_name: repoData.full_name,
        description: repoData.description,
        private: repoData.private,
        default_branch: repoData.default_branch,
        clone_url: repoData.clone_url,
        html_url: repoData.html_url,
        updated_at: repoData.updated_at,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch repository');
    } finally {
      setIsValidating(false);
    }
  };

  // Handle repo connection
  const handleConnect = (repo: RepoListItem) => {
    const [owner, name] = repo.full_name.split('/');

    const repoInfo: VirtualRepoInfo = {
      owner,
      name,
      fullName: repo.full_name,
      defaultBranch: repo.default_branch,
      description: repo.description || undefined,
      isPrivate: repo.private,
      cloneUrl: repo.clone_url,
      lastFetched: new Date().toISOString(),
    };

    onConnect(repoInfo, token);
    onOpenChange(false);
  };

  // Reset state when modal closes
  useEffect(() => {
    if (!open) {
      setSelectedRepo(null);
      setSearchQuery('');
      setRepoUrl('');
      setError(null);
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Github className="h-5 w-5" />
            Connect GitHub Repository
          </DialogTitle>
          <DialogDescription>
            Connect to a GitHub repository to work directly without cloning locally.
            All changes will be made via the GitHub API.
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden flex flex-col gap-4">
          {/* Token Input Section */}
          {!isAuthenticated && (
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="github-token">GitHub Personal Access Token</Label>
                <div className="flex gap-2">
                  <Input
                    id="github-token"
                    type="password"
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    onClick={validateAndFetchRepos}
                    disabled={isValidating || !token.trim()}
                  >
                    {isValidating ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Connect'
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  Create a token at{' '}
                  <a
                    href="https://github.com/settings/tokens/new?scopes=repo"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    github.com/settings/tokens
                  </a>
                  {' '}with "repo" scope.
                </p>
              </div>
            </div>
          )}

          {/* Authenticated State */}
          {isAuthenticated && (
            <>
              <Alert className="border-green-500/50 bg-green-500/10">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <AlertDescription className="text-green-500">
                  Connected to GitHub. Select a repository below.
                </AlertDescription>
              </Alert>

              <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'browse' | 'url')}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="browse">Browse Repositories</TabsTrigger>
                  <TabsTrigger value="url">Enter URL</TabsTrigger>
                </TabsList>

                <TabsContent value="browse" className="mt-4 flex-1 overflow-hidden">
                  {/* Search */}
                  <div className="relative mb-3">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search repositories..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* Repo List */}
                  <ScrollArea className="h-[300px] border rounded-lg">
                    {isLoadingRepos ? (
                      <div className="flex items-center justify-center h-full">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                      </div>
                    ) : filteredRepos.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                        <Github className="h-8 w-8 mb-2 opacity-50" />
                        <p className="text-sm">No repositories found</p>
                      </div>
                    ) : (
                      <div className="p-2 space-y-1">
                        {filteredRepos.map((repo) => (
                          <button
                            key={repo.id}
                            onClick={() => handleConnect(repo)}
                            className="w-full flex items-start gap-3 rounded-lg p-3 text-left transition-colors hover:bg-accent/50 group"
                          >
                            <div className="mt-0.5">
                              {repo.private ? (
                                <Lock className="h-4 w-4 text-yellow-500" />
                              ) : (
                                <Globe className="h-4 w-4 text-muted-foreground" />
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-foreground truncate">
                                  {repo.full_name}
                                </span>
                              </div>
                              {repo.description && (
                                <p className="text-xs text-muted-foreground truncate mt-0.5">
                                  {repo.description}
                                </p>
                              )}
                              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                <GitBranch className="h-3 w-3" />
                                <span>{repo.default_branch}</span>
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </TabsContent>

                <TabsContent value="url" className="mt-4">
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label htmlFor="repo-url">Repository URL</Label>
                      <div className="flex gap-2">
                        <Input
                          id="repo-url"
                          placeholder="https://github.com/owner/repo"
                          value={repoUrl}
                          onChange={(e) => setRepoUrl(e.target.value)}
                          className="flex-1"
                        />
                        <Button
                          onClick={fetchRepoFromUrl}
                          disabled={isValidating || !repoUrl.trim()}
                        >
                          {isValidating ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            'Connect'
                          )}
                        </Button>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Enter a GitHub repository URL to connect directly.
                      Supports HTTPS and SSH URLs.
                    </p>
                  </div>
                </TabsContent>
              </Tabs>
            </>
          )}

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}