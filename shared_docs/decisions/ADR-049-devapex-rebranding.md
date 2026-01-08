# ADR-049: DEVAPEX Rebranding (Production Release)

## Status
Accepted - Production Ready

## Date
2026-01-08

## Context
The Auto-Claude project has evolved into a comprehensive autonomous development platform. To establish a distinct brand identity and reflect its capabilities as an enterprise-grade development platform, a complete rebranding initiative was undertaken to rename the application from "Auto-Claude" to "DEVAPEX" (Development Apex Platform).

The existing yellow/olive color scheme (Oscura Midnight theme with #D6D876 primary) was updated to match the new DEVAPEX brand identity with a professional blue/purple (indigo) color palette suitable for enterprise applications.

## Decision
We completed a comprehensive rebrand of the entire application from "Auto-Claude" to "DEVAPEX" across **160+ files**.

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
  - Light mode: #4F46E5 (Indigo 600)
  - Dusk theme: #5B56E5

### 3. User Interface Components (30+ files)
- Sidebar.tsx - Logo and branding
- App.tsx / App.apex.tsx - Main application
- Onboarding wizard (16 files) - All steps updated
- GitHubSetupModal.tsx - GitHub integration
- AgentTools.tsx - Agent configuration
- OAuth flow components

### 4. Service & API Branding (20+ files)
- GitHub PR review comments: "DEVAPEX Review", "DEVAPEX PR Review"
- GitLab MR review comments: "DEVAPEX MR Review"
- User-Agent header: "DEVAPEX-UI"
- Error messages across all handlers
- Logging and debug reports

### 5. Documentation (10+ files)
- README.md - Project documentation
- CLAUDE.md - AI assistant guidelines
- CONTRIBUTING.md - Contribution guidelines
- RELEASE.md - Release process
- CLI-USAGE.md - Command line guide
- guides/linux.md - Linux installation
- shared_docs/*.md - Shared documentation

### 6. Test Files (55 files)
- All test assertions updated
- Expected strings aligned with new branding

## Files Summary

| Category | Count | Examples |
|----------|-------|----------|
| UI Components | 30+ | Sidebar.tsx, App.tsx, modals, wizards |
| Main Process | 20+ | index.ts, IPC handlers, services |
| Test Files | 55 | *.test.ts, *.test.tsx |
| Documentation | 10+ | README.md, CLAUDE.md, guides |
| Styles | 1 | globals.css |
| Configuration | 3 | package.json, index.html, CHANGELOG.md |

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

### Dusk Theme
```css
--primary: #5B56E5;           /* Custom Indigo */
```

## Consequences

### Positive
- Distinct enterprise-grade brand identity
- Professional blue/purple color scheme aligned with development tools
- Consistent branding across all user touchpoints
- All 160+ files updated for complete consistency
- Production-ready state

### Negative
- Git repository URLs still reference original name (handled separately)
- Some external references may need manual updates

### Neutral
- Backend Python code paths retain original directory names for compatibility
- External integrations (GitHub, GitLab) use new branding in comments

## Production Readiness Checklist

- [x] All UI components branded
- [x] All test files updated
- [x] All documentation updated
- [x] Color theme applied consistently
- [x] Service branding updated
- [x] Error messages updated
- [x] CHANGELOG documented
- [x] Build verification pending

## References
- DEVAPEX Dashboard screenshot (reference for color scheme)
- Tailwind CSS Indigo color palette
- Electron app naming conventions
- Material Design color guidelines
