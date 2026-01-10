# ADR-061: Virtual GitHub Repository Connection Architecture

## Status

Accepted

## Date

2026-01-08

## Context

APEXDEV previously required users to clone GitHub repositories locally before working with them. This created friction for:
- Quick exploration of repositories
- Working with large repositories where full clone is impractical
- Cloud-based or constrained environments
- Rapid prototyping without local storage commitment

## Decision

Implement a Virtual GitHub Repository Connection feature that allows users to connect to and work directly with GitHub repositories via the GitHub Contents API without local cloning.

### Architecture Overview

#### New Type Definitions (project.ts)

`	ypescript
export type ProjectSourceType = 'local' | 'github' | 'gitlab';

export interface VirtualRepoInfo {
  owner: string;
  name: string;
  fullName: string;
  defaultBranch: string;
  description?: string;
  isPrivate: boolean;
  htmlUrl: string;
  cloneUrl: string;
  sshUrl: string;
}

export interface Project {
  // ... existing fields
  sourceType?: ProjectSourceType;
  virtualRepo?: VirtualRepoInfo;
  githubToken?: string;  // Stored for private repo access
}
`

#### IPC Channels (ipc.ts)

New channels for virtual repository operations:
- `GITHUB_VIRTUAL_LIST_FILES` - List directory contents
- `GITHUB_VIRTUAL_GET_FILE` - Read file with base64 decoding
- `GITHUB_VIRTUAL_CREATE_FILE` - Create new file with commit
- `GITHUB_VIRTUAL_UPDATE_FILE` - Update file (requires SHA)
- `GITHUB_VIRTUAL_DELETE_FILE` - Delete file with commit
- `GITHUB_VIRTUAL_GET_TREE` - Recursive directory tree

#### Handler Implementation (virtual-repo-handlers.ts)

Each handler:
1. Validates required parameters (owner, repo, token)
2. Calls GitHub Contents API with authorization header
3. Handles base64 encoding/decoding for file contents
4. Returns structured response with error handling

#### UI Components

- **ConnectGitHubRepoModal**: Modal for connecting to repositories
  - PAT token input with validation
  - Repository list with search/filter
  - Direct URL entry option
  - Private repository indicator

#### Path Convention

Virtual projects use `github://owner/repo` as their path identifier, distinguishing them from local projects with filesystem paths.

### API Endpoints Used

- `GET /user/repos` - List user's repositories
- `GET /repos/{owner}/{repo}/contents/{path}` - List/read contents
- `PUT /repos/{owner}/{repo}/contents/{path}` - Create/update files
- `DELETE /repos/{owner}/{repo}/contents/{path}` - Delete files
- `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` - Full tree

## Consequences

### Positive

- Users can work with repositories without local cloning
- Reduced disk space requirements
- Faster initial project setup
- Enables cloud/constrained environment usage
- Progressive enhancement - can always clone later

### Negative

- Network latency for every file operation
- Rate limiting concerns for GitHub API (5000 req/hour with token)
- No offline capability for virtual projects
- Large file handling limited (GitHub API limits)

### Mitigations

- Implement client-side caching for frequently accessed files
- Show rate limit status in UI
- Clear indication of online/offline status
- Graceful degradation with helpful error messages

## Related ADRs

- ADR-060: APEXDEV Branding Correction and Icon Update
