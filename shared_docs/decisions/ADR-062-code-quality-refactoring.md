# ADR-062: Code Quality Refactoring and Test Infrastructure Alignment

## Status
Accepted

## Date
2026-01-09

## Context

Following the APEXDEV branding migration (ADR-060), the test suite contained 15 failing tests due to directory path mismatches. Additionally, the Python backend had accumulated 4,812 lint errors and the frontend had TypeScript type definition gaps.

### Problems Identified

1. **Test Failures**: 15 tests expected .auto-claude directory but source code used .apexdev
2. **Python Lint Errors**: 4,812 ruff errors across the backend codebase
3. **Syntax Errors**: 2 critical syntax errors blocking imports
4. **Type Exports**: Missing type exports in frontend preload APIs
5. **MCP Server Naming**: Tests referenced uto-claude MCP server instead of pexdev

## Decision

We will execute a comprehensive code quality refactoring following the APEX Refactor methodology:

### Phase 1: Analysis
- Capture baseline metrics (lint errors, test failures)
- Identify hotspots and patterns in failures

### Phase 2: Automated Fixes
- Apply uff format and uff check --fix for Python
- Fix critical syntax errors manually
- Update type exports in frontend

### Phase 3: Test Alignment
- Update all test assertions to use .apexdev directory convention
- Update MCP server name references from uto-claude to pexdev

### Phase 4: Validation
- Run full test suite to verify 100% pass rate
- Document remaining issues for future work

## Implementation

### Python Backend Refactoring

**Syntax Errors Fixed:**
- pps/backend/core/client.py (line 806): Removed misplaced ) in dictionary literal
- pps/backend/skills/review/security_review.py (line 80): Fixed malformed regex pattern

**Automated Fixes Applied:**
- 404 Python files reformatted
- Type annotations modernized: List → list, Dict → dict, Optional[X] → X | None
- Imports sorted (isort compliance)
- Result: 4,812 → 41 errors (99.1% reduction)

### Frontend Type Fixes

- Added Agent type exports to gent-api.ts
- Exposed pex as alias for lectronAPI in preload/index.ts
- Added pex property to global Window interface in ipc.ts
- Fixed AppSettingsDialog export in settings/index.ts
- Fixed ViewType import in Sidebar.tsx

### Test File Updates

| File | Change |
|------|--------|
| test_workspace.py | .auto-claude → .apexdev in worktree path assertions |
| test_worktree.py | Updated worktree directory expectations |
| test_spec_pipeline.py | Updated spec directory path mocks |
| test_project_analyzer.py | Updated security profile path |
| test_security_cache.py | Updated cache file path assertions |
| test_agent_configs.py | MCP server: uto-claude → pexdev |
| test_graphiti.py | Updated db_path assertion for ~/.apexdev/memories |
| test_github_pr_e2e.py | Updated github directory path |
| test_github_pr_review.py | Updated github directory path |

## Consequences

### Positive
- **100% test pass rate**: 2311 passed, 0 failed
- **Cleaner codebase**: 99.1% reduction in Python lint errors
- **Consistent naming**: All references aligned to APEXDEV branding
- **Better maintainability**: Modern Python type annotations

### Negative
- **41 remaining Python errors**: Require manual intervention (E721, W291, UP035, E741)
- **197 TypeScript errors**: Deep architectural issues with ElectronAPI type definitions

### Neutral
- Branch prefix remains uto-claude/ (intentional - affects git history)

## Validation Evidence

`
pytest results: 2311 passed, 0 failed, 1 skipped
ruff check: 41 errors remaining (down from 4,812)
`

## Related Documents
- ADR-060: APEXDEV Branding Correction
- CHANGELOG.md: Version 3.7.6

## Authors
- APEX Refactor Architect (AI-assisted)