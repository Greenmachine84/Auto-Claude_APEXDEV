# ADR-058: API Provider Updates - Gemini and GitHub Copilot

## Status

Accepted

## Date

2026-01-08

## Context

The APEXDEV application requires modern API provider presets for custom API configuration. The original implementation included GLM (China) providers that were region-specific and not widely needed by the target user base.

## Decision

Update the API provider presets to include more commonly used providers:

### Removed

- `glm-global` - GLM Global (<https://api.z.ai/api/anthropic>)
- `glm-cn` - GLM China (<https://open.bigmodel.cn/api/paas/v4>)

### Added

- `gemini` - Google Gemini (<https://generativelanguage.googleapis.com/v1beta>)
- `github-copilot` - GitHub Copilot (<https://api.githubcopilot.com>)

### Retained

- `anthropic` - Anthropic (<https://api.anthropic.com>)
- `openrouter` - OpenRouter (<https://openrouter.ai/api/v1>)
- `groq` - Groq (<https://api.groq.com/openai/v1>)

## Files Changed

- `apps/frontend/src/shared/constants/api-profiles.ts` - Provider definitions
- `apps/frontend/src/shared/i18n/locales/en/settings.json` - English labels
- `apps/frontend/src/shared/i18n/locales/fr/settings.json` - French labels
- `apps/frontend/src/renderer/components/settings/ProfileEditDialog.test.tsx` - Updated tests

## Consequences

### Positive

- Broader provider support for popular APIs
- Simplified preset list without region-specific options
- Better alignment with user needs

### Negative

- Users who were using GLM presets will need to manually configure

## Related ADRs

- ADR-049: APEXDEV Rebranding
