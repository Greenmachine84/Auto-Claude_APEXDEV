# APEXDEV

**Autonomous multi-agent coding framework that plans, builds, and validates software for you.**

![APEXDEV Platform](https://raw.githubusercontent.com/Greenmachine84/Auto-Claude_APEXDEV/upstream-integration/.github/assets/DEVAPEX-Kanban.png)

[![License](https://img.shields.io/badge/license-AGPL--3.0-green?style=flat-square)](./agpl-3.0.txt)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/KCXaPBr4Dj)
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://www.youtube.com/@AndreMikalsen)

---

## 🚀 What is APEXDEV?

APEXDEV is an **AI-powered autonomous development platform** that transforms how you build software. Instead of manually writing every line of code, you describe what you want, and AI agents handle the planning, implementation, testing, and validation.

### Key Capabilities

- **Multi-Agent Orchestration** - Specialized AI agents work in parallel on different tasks
- **Autonomous Development Loop** - From specification to validated code without manual intervention
- **Intelligent Memory** - Agents learn from your codebase and retain context across sessions
- **Safe Experimentation** - All work happens in isolated git worktrees; your main branch stays protected
- **Built-in QA** - Self-validating quality assurance catches issues before human review
- **Smart Merging** - AI-powered conflict resolution when integrating changes

---

## 📥 Download

### Latest Release (v3.7.4)

| Platform | Download |
|----------|----------|
| **Windows** | [APEXDEV-Setup.exe](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/releases) |
| **macOS (Apple Silicon)** | [APEXDEV-arm64.dmg](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/releases) |
| **macOS (Intel)** | [APEXDEV-x64.dmg](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/releases) |
| **Linux (AppImage)** | [APEXDEV-x86_64.AppImage](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/releases) |
| **Linux (Debian)** | [APEXDEV-amd64.deb](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/releases) |

> 📦 All releases include SHA256 checksums and security verification

---

## ⚡ Quick Start

### Prerequisites

- **Claude API Access** - [Get API key](https://console.anthropic.com/)
- **Git Repository** - Your project must be a git repository
- **Node.js 18+** (for development builds)
- **Python 3.11+** (backend agents)

### Installation

1. **Download** the installer for your platform
2. **Launch APEXDEV** and complete the onboarding wizard
3. **Connect Your API** - Configure Claude API credentials
4. **Open a Project** - Select your git repository
5. **Initialize** - Click "Initialize" to create `.apexdev/` directory structure

### Your First Task

1. Navigate to the **Kanban Board**
2. Click **"Create Task"**
3. Describe your feature or fix (e.g., "Add user authentication with JWT")
4. Click **"Start"** and watch AI agents:
   - 📋 Plan the implementation
   - 💻 Write the code
   - ✅ Validate functionality
   - 🔍 Run QA checks
   - 📊 Generate reports

---

## ✨ Features

### 🤖 Autonomous Agents

| Agent Type | Purpose |
|------------|---------|
| **Spec Agent** | Transforms requirements into detailed technical specifications |
| **Coder Agent** | Implements features following specs and best practices |
| **QA Agent** | Validates code quality, tests, and catches regressions |
| **Reviewer Agent** | Performs code review and suggests improvements |
| **Merge Agent** | Intelligently resolves conflicts when integrating changes |

### 🎯 Core Capabilities

- **Parallel Execution** - Run up to 12 agent terminals simultaneously
- **Git Worktrees** - Isolated workspaces for safe parallel development
- **Memory Layer** - Powered by Graphiti for persistent agent knowledge
- **Tracing & Observability** - Built-in LangSmith integration for debugging
- **Multi-Provider Support** - Works with Claude, OpenAI, Ollama, and more

### 🔌 Integrations

- **GitHub** - Import issues, create PRs, sync reviews
- **GitLab** - Merge request workflows and CI/CD integration
- **Linear** - Bi-directional task synchronization
- **Jira** - Issue tracking and sprint management (coming soon)

### 🖥️ User Interface

- **Kanban Board** - Visual task management with real-time agent status
- **Agent Terminals** - Interactive terminals with context injection
- **Roadmap Planner** - AI-assisted feature planning with competitor analysis
- **Insights Chat** - Explore your codebase using natural language
- **Changelog Generator** - Auto-generate release notes from completed work

---

## 📂 Project Structure

```
.apexdev/                    # APEXDEV workspace directory
├── specs/                   # Task specifications
├── ideation/               # AI-generated improvement suggestions
├── insights/               # Codebase exploration results
├── roadmap/                # Feature planning documents
└── memories/               # Persistent agent memory (Neo4j)

apps/
├── backend/                # Python agent framework
│   ├── agents/            # Agent implementations
│   ├── runners/           # Task orchestration
│   ├── spec/              # Specification pipeline
│   ├── merge/             # Merge conflict resolution
│   └── integrations/      # External service connectors
└── frontend/              # Electron desktop application
    ├── src/
    │   ├── main/         # Electron main process
    │   ├── renderer/     # React UI components
    │   └── preload/      # IPC bridge
    └── resources/        # Icons and assets
```

---

## 🛠️ Development

### Build from Source

```bash
# Clone the repository
git clone https://github.com/Greenmachine84/Auto-Claude_APEXDEV.git
cd Auto-Claude_APEXDEV

# Install dependencies
npm run install:all

# Run in development mode
npm run dev

# Build for production
npm run build

# Package for your platform
npm run package
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run install:all` | Install all dependencies (frontend + backend) |
| `npm start` | Build and launch the app |
| `npm run dev` | Development mode with hot reload |
| `npm run build` | Build frontend for production |
| `npm run package` | Create installer for current platform |
| `npm run package:mac` | Package for macOS (DMG) |
| `npm run package:win` | Package for Windows (EXE) |
| `npm run package:linux` | Package for Linux (AppImage, DEB) |
| `npm run lint` | Run ESLint |
| `npm test` | Run frontend tests |
| `npm run test:backend` | Run backend Python tests |

### Backend CLI

For headless operation or CI/CD integration:

```bash
cd apps/backend

# Interactive spec creation
python spec_runner.py --interactive

# Run autonomous build
python run.py --spec 001

# Review and merge
python run.py --spec 001 --review
python run.py --spec 001 --merge
```

See [guides/CLI-USAGE.md](guides/CLI-USAGE.md) for complete CLI documentation.

---

## �� Security

APEXDEV implements a **three-layer security model**:

1. **OS-Level Sandbox** - Commands execute in restricted shell environments
2. **Filesystem Isolation** - Operations limited to project directory
3. **Dynamic Allowlist** - Only approved commands based on detected tech stack

### Additional Protections

- **Prompt Injection Defense** - Input sanitization and validation
- **Secrets Scanning** - Detects API keys and credentials before commits
- **Dependency Auditing** - Automated security checks for packages
- **Code Signing** - Verified releases (macOS, Windows)

All releases undergo:
- VirusTotal scanning
- SHA256 checksum verification
- Automated security testing

---

## 🧪 Testing

### Backend Tests (Python)

```bash
# Run all backend tests with pytest
cd apps/backend
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_workspace.py -v

# Run with coverage
python -m pytest tests/ --cov=apps/backend --cov-report=html
```

### Frontend Tests (Vitest + React Testing Library)

```bash
# Run frontend tests
cd apps/frontend
npm run test

# Run with coverage
npm run test:coverage
```

### Linting & Type Checking

```bash
# Python linting (ruff)
cd apps/backend
ruff check .
ruff format --check .

# TypeScript/ESLint
cd apps/frontend
npm run lint
npm run typecheck
```

### Test Statistics (v3.7.6)

| Component | Tests | Pass Rate |
|-----------|-------|-----------|
| Backend (Python) | 2311 | 100% |
| Frontend (Vitest) | 150+ | 100% |
| E2E Integration | 50+ | 100% |

Test coverage reports available in `coverage/` directory.

---
## 📖 Documentation

- **[CLI Usage Guide](guides/CLI-USAGE.md)** - Headless operation and scripting
- **[Linux Build Guide](guides/linux.md)** - AppImage and Flatpak packaging
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and guidelines
- **[Architecture Decisions](shared_docs/decisions/)** - ADR documentation
- **[Changelog](CHANGELOG.md)** - Version history and release notes

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development environment setup
- Code style and conventions
- Testing requirements
- Pull request guidelines

---

## 💬 Community

- **Discord** - [Join our community](https://discord.gg/KCXaPBr4Dj)
- **Issues** - [Report bugs or request features](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/issues)
- **Discussions** - [Ask questions and share ideas](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/discussions)
- **YouTube** - [Watch tutorials](https://www.youtube.com/@AndreMikalsen)

---

## 📄 License

**AGPL-3.0** - GNU Affero General Public License v3.0

APEXDEV is free and open source. If you modify and distribute it, or run it as a service, your code must also be open source under AGPL-3.0.

Commercial licensing available for closed-source use cases. Contact for details.

---

## 🌟 Star History

If you find APEXDEV helpful, please consider giving us a star! ⭐

[![GitHub Repo stars](https://img.shields.io/github/stars/Greenmachine84/Auto-Claude_APEXDEV?style=social)](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/stargazers)

---

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude](https://anthropic.com/) - AI models
- [Electron](https://electronjs.org/) - Desktop framework
- [React](https://react.dev/) - UI library
- [Graphiti](https://github.com/getzep/graphiti) - Memory layer
- [LangSmith](https://smith.langchain.com/) - Tracing and observability

Special thanks to all [contributors](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/graphs/contributors) who have helped shape APEXDEV!

---

<div align="center">
<strong>Made with 💜 by the APEXDEV Team</strong>
<br/>
<sub>Empowering developers with autonomous AI agents</sub>
</div>