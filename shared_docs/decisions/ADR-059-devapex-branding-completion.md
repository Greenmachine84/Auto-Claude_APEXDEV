# ADR-059: DEVAPEX Branding Completion

## Status

Accepted

## Date

2026-01-08

## Context

Following ADR-049 (DEVAPEX Rebranding), additional legacy "Auto Claude" references were discovered in locale files and the dashboard still displayed internal phase numbers that were not relevant to end users.

## Decision

Complete the branding update across all remaining files:

### Locale Files Updated

- EN: dialogs.json, navigation.json, onboarding.json, settings.json, welcome.json
- FR: dialogs.json, navigation.json, onboarding.json, settings.json, welcome.json

All instances of "Auto Claude" replaced with "DEVAPEX".

### Dashboard UI Polish

- Removed Phase badges (Phase 2-7) from Platform Features cards
- Updated subtitle from "AI-powered development with 10-phase architecture" to "AI-powered autonomous development platform"

## Consequences

### Positive

- Consistent DEVAPEX branding throughout the application
- Cleaner dashboard without internal phase numbers
- Professional appearance for end users

### Negative

- None

## Related ADRs

- ADR-049: DEVAPEX Rebranding
- ADR-058: API Provider Updates
