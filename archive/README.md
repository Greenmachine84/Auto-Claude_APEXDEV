# Archive Directory

> **Purpose**: Store deprecated code, legacy implementations, and superseded documentation for reference.

---

## Directory Structure

```
archive/
├── deprecated/           # Deprecated code modules
│   ├── agents/          # Superseded agent implementations
│   ├── integrations/    # Legacy integration code
│   └── tools/           # Old tool implementations
├── legacy-docs/         # Previous documentation versions
├── pre-merge/           # Code snapshots before major merges
│   └── pre-devapex/     # Auto-Claude state before DEVAPEX integration
└── reference/           # Reference implementations for study
```

---

## APEX Governance Compliance

**Mandate M1.1.1**: Architect folder is IMMUTABLE - this archive preserves history without modifying core specifications.

**Mandate M1.2.1**: All enhancements are ADDITIVE - archived code represents the evolution path, not deletions.

---

## Usage Guidelines

### What Goes Here

1. **Deprecated Code** - Code that has been replaced by newer implementations
2. **Legacy Documentation** - Outdated docs that may still have reference value
3. **Pre-Merge Snapshots** - State captures before significant mergers
4. **Reference Implementations** - Sample code that influenced current design

### What Does NOT Go Here

1. **Active Code** - Anything currently in use
2. **Test Fixtures** - Use `tests/fixtures/` instead
3. **Generated Artifacts** - Build outputs, caches, etc.
4. **Secrets** - Never archive credentials or API keys

---

## Archive Naming Convention

```
{date}_{component}_{version}_deprecated.{ext}

Examples:
- 2026-01-05_task_queue_v1_deprecated.py
- 2026-01-05_memory_store_v2.1_deprecated/
- 2026-01-05_ARCHITECTURE_v1.3_deprecated.md
```

---

## Recovery Process

If archived code needs to be restored:

1. **Review** - Understand why it was archived
2. **Validate** - Ensure it meets current standards
3. **Adapt** - Update for current API compatibility
4. **Test** - Run full test suite
5. **Document** - Update changelog with restoration

---

## Created

- **Date**: 2026-01-05
- **Purpose**: DEVAPEX + Auto-Claude merger preparation
- **Ref**: Auto-Claude_APEXDEV Enhancement Plan
