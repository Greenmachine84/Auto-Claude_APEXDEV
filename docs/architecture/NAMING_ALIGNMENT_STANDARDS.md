# Naming Alignment Standards

> **Auto-Claude_APEXDEV Enhancement Project**
> Naming conventions and terminology alignment guide
> Created: January 6, 2026

---

## Purpose

This document establishes canonical naming standards across all architecture documents, implementation specs, and code to ensure consistency and prevent confusion.

---

## 1. LLM Provider Naming

### Canonical Provider Names (8 Equal Providers)

| Canonical Name | Alternative Names | Usage |
|----------------|-------------------|-------|
| `copilot` | github-copilot, github_copilot, copilot_provider | **Use `copilot`** |
| `openrouter` | open-router, openRouter | **Use `openrouter`** |
| `ollama` | - | **Use `ollama`** |
| `lmstudio` | lm-studio, lm_studio, LMStudio | **Use `lmstudio`** |
| `gemini` | google, google-gemini, google_ai | **Use `gemini`** |
| `openai` | open-ai, openAI | **Use `openai`** |
| `anthropic` | claude, anthropic_claude | **Use `anthropic`** |
| `azure` | azure-openai, azureopenai, azure_openai | **Use `azure`** |

### Provider File Naming Convention

```
apps/backend/llm/providers/
├── copilot_provider.py       # GitHub Copilot
├── openrouter_provider.py    # OpenRouter
├── ollama_provider.py        # Ollama (local)
├── lmstudio_provider.py      # LM Studio (local)
├── gemini_provider.py        # Google Gemini
├── openai_provider.py        # OpenAI Direct
├── anthropic_provider.py     # Anthropic/Claude
└── azure_provider.py         # Azure OpenAI
```

### ⚠️ Deprecation Notice

The following names are **deprecated** and should be migrated:

| Deprecated | Migration | Reason |
|------------|-----------|--------|
| `google_provider.py` | `gemini_provider.py` | Align with product name |
| `groq_provider.py` | Remove or add as 9th provider | Not in canonical 8 |
| `github-copilot` | `copilot` | Simpler, consistent |
| `azure-openai` | `azure` | Shorter, consistent |

---

## 2. Embedding Provider Naming

### Canonical Embedding Provider Names (6 Providers)

| Canonical Name | File Name | Notes |
|----------------|-----------|-------|
| `openai` | `openai_embedder.py` | text-embedding-3 models |
| `ollama` | `ollama_embedder.py` | Local embeddings |
| `voyage` | `voyage_embedder.py` | Voyage AI |
| `gemini` | `gemini_embedder.py` | **Rename from google** |
| `azure` | `azure_embedder.py` | Azure OpenAI embeddings |
| `openrouter` | `openrouter_embedder.py` | OpenRouter embeddings |

### Migration Required

```diff
- apps/backend/llm/embeddings/google_embedder.py
+ apps/backend/llm/embeddings/gemini_embedder.py
```

---

## 3. Authentication Provider Naming

### Canonical Auth Provider Names (4 Equal Providers)

| Canonical Name | Display Name | OAuth Provider |
|----------------|--------------|----------------|
| `github` | GitHub | GitHub OAuth |
| `google` | Google | Google OAuth |
| `microsoft` | Microsoft | Azure AD |
| `manual` | Manual | Username/password |

### Note on `google` vs `gemini`

- **Auth**: Use `google` (OAuth provider name)
- **LLM**: Use `gemini` (product name)

This distinction is intentional - authentication is through Google OAuth, but the LLM product is Gemini.

---

## 4. Agent Naming Conventions

### Core Agents (4)

| Canonical Name | Class Name | File Name |
|----------------|------------|-----------|
| Coder | `CoderAgent` | `coder_agent.py` |
| Reviewer | `ReviewerAgent` | `reviewer_agent.py` |
| Fixer | `FixerAgent` | `fixer_agent.py` |
| Planner | `PlannerAgent` | `planner_agent.py` |

### Enterprise Agents (16)

| Category | Agent Name | Class Name |
|----------|------------|------------|
| Testing | TestWriter | `TestWriterAgent` |
| Testing | TestExecutor | `TestExecutorAgent` |
| Testing | CoverageAnalyzer | `CoverageAnalyzerAgent` |
| DevOps | PipelineBuilder | `PipelineBuilderAgent` |
| DevOps | DeploymentManager | `DeploymentManagerAgent` |
| DevOps | InfraAgent | `InfraAgent` |
| Analysis | SecurityAuditor | `SecurityAuditorAgent` |
| Analysis | PerformanceAnalyzer | `PerformanceAnalyzerAgent` |
| Analysis | DependencyManager | `DependencyManagerAgent` |
| Documentation | DocWriter | `DocWriterAgent` |
| Documentation | APIDocGenerator | `APIDocGeneratorAgent` |
| Documentation | ChangelogBuilder | `ChangelogBuilderAgent` |
| Integration | GitHubAgent | `GitHubAgent` |
| Integration | GitLabAgent | `GitLabAgent` |
| Integration | LinearAgent | `LinearAgent` |
| Integration | SlackAgent | `SlackAgent` |

---

## 5. Module/Package Naming

### Directory Naming (snake_case)

```
apps/backend/
├── agents/                   # Agent system
├── memory/                   # Memory system
├── llm/                      # LLM providers
├── skills/                   # Skills framework
├── tools_pkg/                # Tools (existing name preserved)
├── orchestrator/             # Orchestration
├── security/                 # Security module
├── governance/               # Governance engine
├── analytics/                # Analytics system
└── integrations/             # External integrations
```

### File Naming (snake_case)

- Classes: `class_name.py` (e.g., `coder_agent.py`)
- Types: `*_types.py` (e.g., `memory_types.py`)
- Providers: `*_provider.py` or `*_embedder.py`
- Tests: `test_*.py`

---

## 6. Configuration Key Naming

### Environment Variables (SCREAMING_SNAKE_CASE)

| Provider | API Key Variable |
|----------|-----------------|
| copilot | `GITHUB_TOKEN` |
| openrouter | `OPENROUTER_API_KEY` |
| ollama | (none - local) |
| lmstudio | (none - local) |
| gemini | `GOOGLE_API_KEY` |
| openai | `OPENAI_API_KEY` |
| anthropic | `ANTHROPIC_API_KEY` |
| azure | `AZURE_OPENAI_API_KEY` |

### Config File Keys (snake_case)

```json
{
  "llm_providers": {
    "default": "openrouter",
    "copilot": { "enabled": true },
    "openrouter": { "api_key": "..." },
    "gemini": { "api_key": "..." }
  }
}
```

---

## 7. Inconsistencies to Fix

### Phase 2 Architecture

| Current | Should Be | Location |
|---------|-----------|----------|
| `google_provider.py` | `gemini_provider.py` | `llm/providers/` |
| `google_embedder.py` | `gemini_embedder.py` | `llm/embeddings/` |
| `groq_provider.py` | Remove or document as additional | Not in canonical 8 |
| "7 providers" | "8 providers" | Documentation text |

### PRD Document

| Current | Should Be | Section |
|---------|-----------|---------|
| "7+ routers" | "8 equal providers" | §1.3 |
| "LMStudio" | "lmstudio" | §4.2 |
| "GitHub Copilot" (display) | Keep for display, use `copilot` in code | Throughout |

### Phase 6 Security

Already aligned with canonical naming ✅

---

## 8. Implementation Checklist

When implementing code, verify:

- [ ] Provider names match canonical list
- [ ] File names follow `{provider}_provider.py` pattern
- [ ] Environment variables match standard names
- [ ] Config keys use snake_case
- [ ] Class names use PascalCase
- [ ] 8 LLM providers referenced (not 7)
- [ ] `gemini` used for LLM, `google` only for auth

---

## 9. Cross-Reference Updates Needed

| Document | Update Required |
|----------|-----------------|
| PHASE2_MEMORY_LLM_ARCHITECTURE.md | Rename google → gemini, clarify groq |
| PRD_DEVAPEX_INTEGRATION.md | Update "7+ routers" to "8 equal providers" |
| PHASE6_SECURITY_ARCHITECTURE.md | ✅ Already aligned |
| Implementation code | Follow canonical naming |

---

*This document is authoritative for naming conventions.*
*All new code and documentation MUST follow these standards.*
