/**
 * APEX Development Platform - Services Index
 * Phase 4: UI, Integrations & Analytics
 *
 * Export all main process services.
 */

export { BackendService } from './backend-service';
export { GitService, type GitStatusEntry, type GitBranch, type GitCommit, type GitDiff } from './git-service';
export { TerminalService, type TerminalSession, type TerminalOutput } from './terminal-service';
export { NotificationService, type NotificationType, type NotificationOptions, type NotificationRecord } from './notification-service';
