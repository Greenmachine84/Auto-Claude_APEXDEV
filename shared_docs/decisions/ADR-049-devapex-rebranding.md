# ADR-049: DEVAPEX Rebranding

## Status
Accepted

## Date
2026-01-08

## Context
The Auto-Claude project has evolved into a comprehensive autonomous development platform. To better reflect its capabilities and establish a distinct brand identity, a rebranding initiative was undertaken to rename the application from "Auto-Claude" to "DEVAPEX" (Development Apex Platform).

The existing yellow/olive color scheme (Oscura Midnight theme with #D6D876 primary) needed updating to match the new DEVAPEX brand identity with a professional blue/purple (indigo) color palette.

## Decision
We will rebrand the entire application from "Auto-Claude" to "DEVAPEX" including:

### 1. Core Application Identity
- Window title: "DEVAPEX - Autonomous Coding Platform"
- App name in Electron: "DEVAPEX"
- Package name: "devapex-ui"
- Author: "DEVAPEX Team"

### 2. Visual Branding
- New sidebar logo with "D" icon box and "DEVAPEX" text
- Updated color scheme to indigo/purple palette:
  - Primary: #6366F1 (Indigo 500)
  - Primary Foreground: #FFFFFF
  - Accent: #1E1B4B (Indigo 950)
  - Accent Foreground: #A5B4FC (Indigo 300)
  - Ring/Focus: #6366F1

### 3. User-Facing Text
- GitHub PR review comments: "DEVAPEX Review", "DEVAPEX PR Review"
- GitLab MR review comments: "DEVAPEX MR Review"
- Error messages referencing the platform
- User-Agent header: "DEVAPEX-UI"

## Files Modified

### Core Branding
| File | Change |
|------|--------|
| `apps/frontend/src/renderer/index.html` | Title → "DEVAPEX - Autonomous Coding Platform" |
| `apps/frontend/src/main/index.ts` | app.setName/app.name → "DEVAPEX" |
| `apps/frontend/package.json` | name, description, author updated |
| `apps/frontend/src/renderer/components/Sidebar.tsx` | New logo component |

### Color Theme
| File | Change |
|------|--------|
| `apps/frontend/src/renderer/styles/globals.css` | All theme colors updated (dark, light, dusk) |

### Service Branding
| File | Change |
|------|--------|
| `apps/frontend/src/main/ipc-handlers/github/pr-handlers.ts` | PR review branding |
| `apps/frontend/src/main/ipc-handlers/gitlab/mr-review-handlers.ts` | MR review branding |
| `apps/frontend/src/main/ipc-handlers/github/utils.ts` | User-Agent header |
| `apps/frontend/src/main/ipc-handlers/task/execution-handlers.ts` | Error messages |
| `apps/frontend/src/main/ipc-handlers/task/worktree-handlers.ts` | Error messages |
| `apps/frontend/src/main/insights/insights-executor.ts` | Error messages |

## Color Palette

### Dark Mode (Primary Theme)
```css
--primary: #6366F1;           /* Indigo 500 */
--primary-foreground: #FFFFFF;
--accent: #1E1B4B;            /* Indigo 950 */
--accent-foreground: #A5B4FC; /* Indigo 300 */
--ring: #6366F1;
```

### Light Mode
```css
--primary: #4F46E5;           /* Indigo 600 */
--ring: #4F46E5;
```

## Consequences

### Positive
- Distinct brand identity separate from Claude/Anthropic branding
- Professional blue/purple color scheme aligned with development tools aesthetics
- Consistent branding across all user touchpoints (UI, PR comments, error messages)
- Clear platform identity: "DEVAPEX - Autonomous Coding Platform"

### Negative
- Existing documentation and references may still use "Auto-Claude"
- Users familiar with old branding may need orientation
- Some internal code comments may still reference old name

### Neutral
- Backend code paths/directories retain original names for compatibility
- Git repository name unchanged (handled separately)

## References
- DEVAPEX Dashboard screenshot (reference for color scheme)
- Tailwind CSS Indigo color palette
- Electron app naming conventions
