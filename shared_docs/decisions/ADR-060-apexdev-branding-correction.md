# ADR-060: APEXDEV Branding Correction and Icon Update

## Status

Accepted

## Date

2026-01-08

## Context

During the rebranding process from Auto-Claude, the branding was incorrectly changed to "DEVAPEX" instead of the correct "APEXDEV". Additionally, the application was still using the original Auto-Claude icons.

## Decision

### Branding Correction

Changed all instances of "DEVAPEX" to "APEXDEV" across:
- All locale files (EN/FR: dialogs, navigation, onboarding, settings, welcome)
- UI components (Sidebar, Worktrees, GitHubSetupModal, App, AppUpdateNotification)
- Onboarding components (ClaudeCodeStep, FirstSpecStep, OllamaModelSelector, GraphitiStep, DevToolsStep, MemoryStep)
- Logger and test files
- ADR documents (ADR-058, ADR-059)
- CHANGELOG entries

### Icon Updates

Created new APEXDEV-branded icons with:
- **Design**: Modern indigo/purple gradient with an "A" apex symbol
- **Color scheme**: Indigo (#6366F1) with purple (#8B5CF6) and blue (#3B82F6) accents
- **Symbol**: Stylized "A" representing apex/peak, with a pinnacle dot

Generated icon files:
- `icon.ico` - Windows icon (16x16, 32x32, 48x48, 256x256)
- `icon.png` - Main 512x512 PNG
- `icon-256.png` - Development icon
- `icon-1024.png` - High-resolution source for ICNS conversion
- `icons/*.png` - Linux icons (16, 32, 48, 64, 128, 256, 512)

### Backend Directory Structure Migration

Migrated backend Python codebase from .auto-claude to .apexdev directory structure across 83+ files:

**Core Systems:**
- pps/backend/init.py - Project initialization utilities
- pps/backend/core/ - Client and workspace management
- pps/backend/cli/ - Batch commands and utilities

**Agent Systems:**
- pps/backend/agents/ - Tools, permissions, and utilities

**Integration Systems:**
- pps/backend/integrations/graphiti/ - Configuration and tests
- pps/backend/memory/ - Memory paths
- pps/backend/services/ - Context services

**Runner Systems:**
- pps/backend/runners/ - GitHub, GitLab, insights, roadmap, spec runners
- pps/backend/security/ - Configuration and constants
- pps/backend/spec/pipeline/ - Models and orchestrator

**Frontend Consistency:**
- pps/frontend/src/main/project-initializer.ts - Lowercase .apexdev consistency (.APEXDEV -> .apexdev)

This migration fixed the Initialize button functionality and enabled Agent/Skill/Command creation by aligning the backend directory structure with the frontend.

### Path/Directory Names

Updated directory references:
- `.devapex/` -> `.apexdev/`
- `devapex/task-name` -> `apexdev/task-name`
- `~/.devapex/` -> `~/.apexdev/`

## Consequences

### Positive

- Consistent "APEXDEV" branding throughout the application
- Professional, modern icon design aligned with the brand
- Clear visual distinction from the original Auto-Claude

### Negative

- Requires users with existing `.devapex/` directories to rename them
- macOS `.icns` file requires conversion on macOS or using third-party tools

## Related ADRs

- ADR-058: API Provider Updates
- ADR-059: APEXDEV Branding Completion


