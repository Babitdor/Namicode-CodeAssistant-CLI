# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nami-Code is an open-source terminal-based AI coding assistant similar to Claude Code. It's built on the `nami-deepagents` library (located in `deepagents-nami/`), which implements a "Deep Agent" architecture with planning tools, subagent delegation, file system access, and detailed prompts.

## Development Commands

### Running the CLI
```bash
# Run during development
uv run nami

# Run with reinstall
make run_reinstall
```

### Testing
```bash
# Run unit tests (with socket disabled for isolation)
make test

# Run specific test file
make test TEST_FILE=tests/unit_tests/test_specific.py

# Run integration tests
make test_integration

# Run all tests
make test_all

# Run tests with coverage
make test_cov

# Watch mode for tests
make test_watch
```

### Code Quality
```bash
# Format code (ruff format + ruff check --fix)
make format

# Check linting (without fixing)
make lint
```

### Cleanup
```bash
make clean  # Remove build artifacts, caches, egg-info
```

## Architecture

### Deep Agent Pattern

Nami-Code implements the "Deep Agent" architecture with four core components:

1. **Planning tool** (`write_todos`) - Task decomposition and tracking
2. **Subagents** (`task` tool) - Parallel delegation with context isolation
3. **File system access** - Context offloading via CompositeBackend (local + sandbox)
4. **Detailed prompts** - Persistent memory via agent.md files

### Key Modules

**Entry Point & CLI Loop** (`main.py`)
- Command-line parsing and validation
- Interactive REPL with prompt_toolkit
- Session management (save/restore with auto-save every 5 min or 5 messages)
- Command handling (`/help`, `/tokens`, etc.)
- Integration with sandbox backends

**Agent Creation** (`agent.py`)
- Uses `nami_deepagents.create_deep_agent()` from the local deepagents library
- Builds LangGraph Pregel graphs with middleware stack
- Manages agent profiles in `~/.nami/agents/<name>/agent.md`
- Shared InMemoryStore for agent/subagent communication
- File tracker for context-aware operations

**Task Execution** (`execution.py`)
- Streaming execution with real-time output
- Human-in-the-loop approval for destructive operations
- Tool call visualization with diff previews
- Token tracking and context management

**Configuration** (`config.py`)
- Settings management (models, providers, auto-approve, etc.)
- Color schemes and UI constants
- Model creation (OpenAI, Anthropic, Ollama, Google)

**Middleware Stack** (applied in order during agent creation)
1. `ShellMiddleware` (`shell.py`) - Shell command execution
2. `SkillsMiddleware` (`skills/middleware.py`) - Progressive disclosure skill system
3. `MCPMiddleware` (`mcp/middleware.py`) - Model Context Protocol integration
4. `AgentMemoryMiddleware` (`agent_memory.py`) - Persistent agent memory
5. `SharedMemoryMiddleware` (`shared_memory.py`) - Cross-agent communication
6. `FileTrackerMiddleware` (`file_tracker.py`) - Track file operations

### Backend Architecture

**CompositeBackend Pattern**
The agent uses a `CompositeBackend` combining:
- `FilesystemBackend` - Local file operations
- `SandboxBackend` - Remote execution (Modal, Runloop, Daytona, Docker)

Backends are wrapped with:
- `StateBackend` - Exposes state to tools
- `StoreBackend` - Exposes LangGraph store to tools

### Sandbox Integrations

All sandbox providers in `namicode_cli/integrations/`:
- `modal.py` - Modal sandbox
- `runloop.py` - Runloop sandbox
- `daytona.py` - Daytona workspace
- `docker.py` - Docker containers
- `sandbox_factory.py` - Factory for creating sandbox instances

### Skills System

**Location**: `namicode_cli/skills/`

Skills follow Anthropic's progressive disclosure pattern:
- Metadata (name + description) injected into system prompt
- Full instructions loaded from `SKILL.md` when needed
- Supports both global (`~/.nami/agents/{AGENT_NAME}/skills/`) and project-specific (`.nami/skills/`) skills

**Structure**:
```
~/.nami/agents/default/skills/
├── web-research/
│   ├── SKILL.md        # YAML frontmatter + instructions
│   └── helper.py       # Optional supporting files
```

### MCP Integration

**Location**: `namicode_cli/mcp/`

Model Context Protocol servers extend agent capabilities:
- `client.py` - MultiServerMCPClient for managing connections
- `middleware.py` - Injects MCP tools into agent
- `presets.py` - Preset configurations (filesystem, github, postgres, etc.)
- `commands.py` - CLI commands for MCP management

MCP tools are namespaced: `servername__toolname` (e.g., `github__search_repos`)

### Memory Systems

**Agent Memory** (`agent_memory.py`)
- Persistent memory across sessions via `agent.md` files
- Global: `~/.nami/agents/default/agent.md`
- Project: `.nami/NAMI.md`

**Shared Memory** (`shared_memory.py`)
- Cross-agent communication via InMemoryStore
- Memory entries include attribution (author, timestamp, tags)
- Shared between main agent and all subagents
- Namespace: `("shared_memory",)`

**File Tracker** (`file_tracker.py`)
- Tracks read/write operations during session
- Provides context-aware file operation suggestions
- Session-scoped tracking (reset on new session)

### Tool System

Built-in tools from `nami-deepagents`:
- File operations: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
- Planning: `write_todos`
- Delegation: `task` (spawns subagents)
- Web: `web_search`, `fetch_url` (from `tools.py`)
- Execution: `execute_bash` (local) or `execute` (sandbox)

Additional tools:
- `dev_server.py` - Dev server management tools
- `test_runner.py` - Test execution tools

## Important Development Patterns

### Working with deepagents-nami

The `deepagents-nami/` directory is a **local dependency** linked via:
```toml
[tool.uv.sources]
nami-deepagents = { path = "./deepagents-nami" }
```

When modifying deepagents functionality:
1. Make changes in `deepagents-nami/nami_deepagents/`
2. Changes are immediately available to `namicode_cli/` (no reinstall needed with `uv run`)
3. Run tests from both directories if applicable

### Middleware Development

When creating new middleware:
1. Inherit from `AgentMiddleware`
2. Define state schema extending `AgentState`
3. Implement `__call__` to wrap model requests/responses
4. Add to middleware stack in `agent.py:create_agent_with_config()`
5. Order matters - middleware is applied sequentially

### Testing Conventions

- Unit tests: `tests/unit_tests/` (socket disabled via `--disable-socket`)
- Integration tests: `tests/integration_tests/`
- Use `pytest` with timeout (default 10s per test)
- Per-file ignores configured in `pyproject.toml` (e.g., allow print in CLI files)

### Code Style

- Ruff with ALL rules enabled, specific ignores in `pyproject.toml`
- Google-style docstrings
- Type hints required (mypy strict mode with reduced strictness on generics)
- Line length: 100 characters

### Error Handling

`namicode_cli/errors/` contains error handling utilities:
- Use rich formatting for user-facing errors
- Provide actionable error messages
- Handle sandbox-specific errors gracefully

## Project Structure

```
namicode_cli/
├── main.py              # CLI entry point and REPL loop
├── agent.py             # Agent creation and configuration
├── execution.py         # Task execution and streaming
├── config.py            # Settings and model creation
├── tools.py             # Custom tool implementations
├── ui.py                # Rich-based UI rendering
├── commands.py          # CLI command handlers
├── input.py             # User input handling with prompt_toolkit
├── skills/              # Progressive disclosure skill system
│   ├── middleware.py    # Skills middleware
│   ├── load.py          # Skill loading and metadata parsing
│   └── commands.py      # Skill management commands
├── mcp/                 # Model Context Protocol integration
│   ├── middleware.py    # MCP middleware
│   ├── client.py        # MultiServerMCPClient
│   ├── presets.py       # Preset configurations
│   └── commands.py      # MCP management commands
├── integrations/        # Sandbox provider implementations
│   ├── sandbox_factory.py
│   ├── modal.py
│   ├── runloop.py
│   ├── daytona.py
│   └── docker.py
├── agent_memory.py      # Persistent agent memory
├── shared_memory.py     # Cross-agent communication
├── file_tracker.py      # File operation tracking
├── shell.py             # Shell execution middleware
├── subagent.py          # Subagent creation utilities
└── errors/              # Error handling

deepagents-nami/         # Core agent library (local dependency)
├── nami_deepagents/
│   ├── agent.py         # create_deep_agent() implementation
│   ├── backends/        # Backend abstractions
│   └── tools/           # Built-in tools

evaluation/              # Terminal-Bench evaluation framework
```

## Configuration Files

- `pyproject.toml` - Project metadata, dependencies, tool configuration (ruff, pytest, mypy)
- `Makefile` - Development commands
- `.env` - API keys and environment variables (not in git)
- `.env.template` - Template for environment setup

## Memory File Locations

- Global agent: `~/.nami/agents/default/agent.md`
- Project agent: `.nami/NAMI.md` or `.claude/CLAUDE.md`
- Skills: `~/.nami/agents/default/skills/` (global), `.nami/skills/` (project)
- MCP config: `~/.nami/mcp-config.json`
