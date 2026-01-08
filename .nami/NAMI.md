# NAMI.md

This file provides guidance to AI assistants when working with code in this repository.

## Project Overview

Nami-Code CLI is an open-source terminal-based AI coding assistant similar to Claude Code. It provides a rich command-line interface for AI-powered code assistance with built-in tools, customizable skills, persistent memory, and project awareness.

The CLI is built on top of the `deepagents` library (located in the `deepagents-nami/` subdirectory), which implements a "Deep Agent" architecture with four key components:
1. **Planning tool** (`write_todos`) for task management
2. **Sub-agents** (`task` tool) for parallel delegation and context isolation
3. **File system access** via multiple backends (local, sandbox)
4. **Detailed prompts** with memory and skills systems

## Technology Stack

- **Language**: Python 3.11+
- **Core Framework**: LangChain and LangGraph (for agent orchestration)
- **Deep Agents**: Custom `nami-deepagents` library (local dependency in `deepagents-nami/`)
- **Terminal UI**: Rich library for beautiful CLI output
- **LLM Providers**:
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - Ollama (local models)
  - Google (Gemini models)
- **Sandbox Providers**: Modal, Runloop, Daytona, Docker
- **Extensibility**: Model Context Protocol (MCP)
- **Package Management**: uv (recommended) or pip
- **Code Quality**: Ruff (linting/formatting), MyPy (type checking), pytest (testing)

## Project Structure

```
namicode-codeassistant-cli/
├── namicode_cli/              # Main CLI package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point
│   ├── main.py               # CLI loop and argument parsing
│   ├── agent.py              # Agent creation and configuration
│   ├── config.py             # Settings, environment, constants
│   ├── execution.py          # Task execution and streaming
│   ├── tools.py              # Custom tool implementations
│   ├── ui.py                 # Rich-based UI rendering
│   ├── commands.py           # Interactive command handlers
│   ├── input.py              # Input handling (prompt_toolkit)
│   ├── model_manager.py      # LLM provider management
│   ├── agent_memory.py       # Agent memory middleware
│   ├── skills/               # Skills system (progressive disclosure)
│   │   ├── commands.py       # Skill management commands
│   │   ├── load.py           # Skill loading logic
│   │   └── middleware.py     # Skills integration middleware
│   ├── mcp/                  # Model Context Protocol integration
│   │   ├── client.py         # MCP client implementation
│   │   ├── commands.py       # MCP management commands
│   │   ├── config.py         # MCP configuration
│   │   ├── middleware.py     # MCP integration middleware
│   │   └── presets.py        # Pre-configured MCP servers
│   ├── integrations/         # Sandbox provider integrations
│   │   ├── sandbox_factory.py # Sandbox backend factory
│   │   ├── modal.py          # Modal sandbox provider
│   │   ├── runloop.py        # Runloop sandbox provider
│   │   ├── daytona.py        # Daytona sandbox provider
│   │   └── docker.py         # Docker sandbox provider
│   ├── errors/               # Error handling and taxonomy
│   ├── file_ops.py           # File operation tools
│   ├── shell.py              # Shell command execution
│   ├── session_persistence.py # Session save/restore
│   ├── session_restore.py    # Session restoration logic
│   ├── project_utils.py      # Project detection utilities
│   └── default_agent_prompt.md # Default system prompt
├── deepagents-nami/          # Core deepagents library (local dependency)
│   ├── nami_deepagents/      # Library package
│   │   ├── graph.py          # Main create_deep_agent() factory
│   │   ├── middleware/       # Middleware implementations
│   │   │   ├── filesystem.py   # FilesystemMiddleware
│   │   │   ├── subagents.py    # SubAgentMiddleware
│   │   │   └── patch_tool_calls.py
│   │   └── backends/         # Storage backends
│   │       ├── filesystem.py   # File system storage
│   │       ├── state.py       # State storage
│   │       ├── store.py       # LangGraph Store backend
│   │       ├── sandbox.py     # Sandbox backend
│   │       ├── composite.py   # Composite backend
│   │       ├── protocol.py    # Backend protocols
│   │       └── utils.py       # Backend utilities
│   ├── pyproject.toml        # Library configuration
│   └── Makefile              # Development commands
├── tests/                    # Test suite
│   ├── unit_tests/           # Unit tests
│   └── integration_tests/    # Integration tests
├── assets/                   # Static assets (banners, images)
├── pyproject.toml            # Project configuration (Ruff, pytest, etc.)
├── setup.py                  # Package setup and entry points
├── Makefile                  # Development commands
├── README.md                 # User documentation
├── .env.template             # Environment variable template
└── LICENSE                   # MIT License
```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/Babitdor/namicode-cli.git
cd namicode-cli

# Create virtual environment and install dependencies
uv venv
uv pip install -e .
```

### API Keys Setup

Copy `.env.template` to `.env` and configure your preferred LLM provider:

```bash
# OpenAI (default)
OPENAI_API_KEY=your-openai-api-key

# Or Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional: Web search (Tavily)
TAVILY_API_KEY=your-tavily-api-key

# Optional: Sandbox providers
RUNLOOP_API_KEY=your-runloop-key
DAYTONA_API_KEY=your-daytona-key
```

## Development Commands

### Running the CLI

```bash
# Development mode
uv run nami

# With specific agent
uv run nami --agent mybot

# Auto-approve tools (skip approval prompts)
uv run nami --auto-approve

# Use sandbox
uv run nami --sandbox modal
```

### Testing

```bash
# Run all unit tests
make test
# Or
uv run pytest tests/unit_tests

# Run specific test file
make test TEST_FILE=tests/unit_tests/test_specific.py

# Run integration tests
make test_integration

# Watch mode (auto-run on file changes)
make test_watch
```

### Code Quality

```bash
# Format code with Ruff
make format

# Check linting
make lint

# Format with unsafe fixes
make format_unsafe
```

### Deepagents Library (deepagents-nami/)

The `deepagents-nami/` directory contains the core deepagents library that this CLI depends on. To work on it:

```bash
cd deepagents-nami

# Install in development mode
uv pip install -e .

# Run tests
uv run pytest
```

## Architecture

### Deep Agent Architecture

The CLI implements a "Deep Agent" pattern inspired by Claude Code, designed to handle complex multi-step tasks:

1. **Planning Tool**: `write_todos` enables the agent to create and manage structured task lists for complex work
2. **Sub-Agents**: The `task` tool allows spawning ephemeral subagents for parallel execution and context isolation
3. **File System Access**: Multiple backends support local filesystem operations and sandbox execution
4. **Detailed Prompts**: System prompts incorporate persistent memory (agent.md), skills, and project context

### Key Components

**Agent Creation** (`agent.py`):
- `create_agent_with_config()` - Main factory function for creating configured agents
- `list_agents()` - List available agent configurations
- `reset_agent()` - Reset or copy agent configurations

**Configuration** (`config.py`):
- Environment variable loading (via python-dotenv)
- LLM provider detection and model creation
- Project root detection (finds .git directory)
- Memory file discovery (agent.md, CLAUDE.md, NAMI.md)
- Interactive commands registry

**Execution** (`execution.py`):
- Task execution with streaming output
- Tool usage tracking and approval
- Error handling and recovery

**Tools** (`tools.py`):
- Built-in tools: `http_request`, `fetch_url`, `web_search`
- File operations: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
- Execution: `shell` (local), `execute` (sandbox)
- Dev tools: `start_dev_server_tool`, `stop_dev_server_tool`, `list_servers_tool`, `run_tests_tool`

- **Middleware System**:
- `AgentMemoryMiddleware` - Loads and updates agent.md files with user feedback
- `SkillsMiddleware` - Progressive disclosure skill loading
- `MCPMiddleware` - Model Context Protocol tool integration
- `ShellMiddleware` - Command execution handling
- `TodoListMiddleware` - Planning with write_todos tool
- `HumanInTheLoopMiddleware` - Tool approval and interrupt handling
- `AnthropicPromptCachingMiddleware` - Optimizes token usage with Anthropic models

**Skills System** (`skills/`):
- Progressive disclosure pattern: agent knows skills exist but only loads instructions when needed
- Skills stored in `~/.nami/skills/` (global) or `.nami/skills/` (project-specific)
- Each skill has a `SKILL.md` with instructions and optional helper scripts

**MCP Integration** (`mcp/`):
- Supports HTTP and stdio transports
- Pre-configured presets for common MCP servers
- Dynamic tool loading from MCP servers

**Sandbox Backends** (`integrations/`):
- `Modal` - Cloud sandbox via Modal platform
- `Runloop` - Cloud sandbox via Runloop API
- `Daytona` - Development environment sandbox
- `Docker` - Local Docker container sandbox
- `CompositeBackend` - Combines multiple backends intelligently

### Memory System

The agent maintains persistent memory through `agent.md` files:

- **Global Memory** (`~/.nami/agents/default/agent.md`): Personality, style, universal preferences
- **Project Memory** (`.nami/agent.md` or `.nami/CLAUDE.md`): Project-specific context, conventions, architecture

Memory is automatically updated when the user describes preferences or gives feedback.

## Important Files

### Core Files
- `namicode_cli/main.py` - CLI entry point, argument parsing, main interaction loop
- `namicode_cli/agent.py` - Agent creation, configuration, and management
- `namicode_cli/config.py` - Settings, environment, project detection, model creation
- `namicode_cli/execution.py` - Task execution, streaming, tool approval
- `namicode_cli/tools.py` - Custom tool implementations
- `namicode_cli/ui.py` - Rich-based terminal UI rendering

### Configuration Files
- `pyproject.toml` - Project configuration (Ruff, pytest, MyPy settings)
- `setup.py` - Package setup, dependencies, entry points
- `.env.template` - Environment variable template
- `Makefile` - Development commands (test, format, lint)

### Deepagents Library
- `deepagents-nami/nami_deepagents/` - Core deepagents implementation
- `deepagents-nami/pyproject.toml` - Library configuration

### Documentation
- `README.md` - User-facing documentation
- `namicode_cli/default_agent_prompt.md` - Default system prompt

## Common Workflows

### Adding a New Tool

1. Implement the tool function in `namicode_cli/tools.py` or create a new module
2. Add proper type hints and docstrings
3. Register the tool in the agent creation logic in `namicode_cli/agent.py`
4. Test the tool with the agent

### Creating a Custom Skill

```bash
# Create a new skill
uv run nami skills create my-skill

# Create a project-specific skill
uv run nami skills create my-skill --project
```

The skill will be created in `~/.nami/skills/my-skill/SKILL.md` (global) or `.nami/skills/my-skill/SKILL.md` (project).

### Adding an MCP Server

```bash
# Add a preset MCP server
uv run nami mcp add filesystem-server --preset filesystem

# Add a custom MCP server
uv run nami mcp add docs-server --transport http --url https://example.com/mcp
```

### Working with the Deepagents Library

The `deepagents-nami/` directory is a local dependency. Changes to it affect the CLI immediately:

1. Make changes in `deepagents-nami/nami_deepagents/`
2. Reinstall the CLI to pick up changes: `uv pip install -e .`

### Running in Debug Mode

Set environment variable for verbose logging:

```bash
export DEEP_AGENTS_DEBUG=1
uv run nami
```

## Testing

### Test Structure

- `tests/unit_tests/` - Unit tests for individual components
- `tests/integration_tests/` - Integration tests for full workflows

### Running Tests

```bash
# All unit tests
make test

# Specific test file
make test TEST_FILE=tests/unit_tests/test_agent.py

# Integration tests (may require API keys)
make test_integration

# Watch mode
make test_watch
```

### Test Configuration

- Default timeout: 10 seconds (configurable in pyproject.toml)
- Tests use `pytest-socket` to disable network access by default
- Integration tests can use network when needed

### Testing Philosophy

- Unit tests focus on individual functions and components
- Integration tests verify end-to-end workflows
- Mock external dependencies (LLM APIs, sandbox providers) when possible
- Use pytest fixtures for common test setup

## Code Style and Conventions

### Formatting and Linting

- **Line Length**: 100 characters (configured in pyproject.toml)
- **Style Guide**: Google-style docstrings (pydocstyle convention)
- **Linter**: Ruff with all rules enabled (with specific ignores)
- **Type Checking**: MyPy in strict mode
- **Comments**: Always use proper comments when writing code - Add descriptive comments explaining logic, purpose, and implementation details

### Ruff Configuration

Key ignored rules (see `pyproject.toml`):
- `COM812`, `ISC001` - Conflicts with formatter
- `SLF001` - Private member access (used for testing)
- `PLR0913` - Too many function arguments (necessary for some tools)
- `C901` - Function complexity (occasionally needed)

### Per-File Ignores

- `namicode_cli/cli.py` - Allows print statements (`T201`)
- `tests/*` - Relaxed documentation, allows asserts, etc.

### Naming Conventions

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### Type Hints

- All functions should have type hints
- Use `|` for union types (Python 3.11+)
- Optional types: `T | None` instead of `Optional[T]`
- Use `typing.Literal` for string enums

## Additional Notes

### Dependency Management

- The project uses `uv` for fast dependency resolution
- `nami-deepagents` is a local dependency from `deepagents-nami/`
- PyPI version is used when `deepagents-nami/` is not present (production)

### Session Persistence

- Sessions are auto-saved every 5 minutes or after 5 new messages
- Manual save with `/save` command
- Sessions are restored when restarting the CLI
- Session files are stored in project-specific directories

### Project Detection

The CLI automatically detects project roots by looking for:
- `.git` directory (indicates Git repository)
- `.nami/` directory (Nami-specific configuration)
- `.claude/` directory (Claude Code compatibility)

### Memory-First Protocol

When working with this codebase as an AI assistant:

1. **At session start**: Check `~/.nami/agents/nami-agent/agent.md` for your personal preferences
2. **Before answering**: Check `.nami/agent.md` in the project directory for project-specific context
3. **When learning**: Update the appropriate memory file when you learn new information

### Sandbox Execution

The CLI supports multiple sandbox backends for safe code execution:
- **Modal**: Cloud-based, requires Modal account
- **Runloop**: Cloud-based, requires Runloop API key
- **Daytona**: Development environment, requires Daytona API key
- **Docker**: Local container, requires Docker daemon

Use the `--sandbox` flag to specify the backend.

### Platform Compatibility

- Windows: UTF-8 encoding forced for Rich console output
- Linux/macOS: Standard encoding
- Paths: Use `pathlib.Path` for cross-platform compatibility

### Entry Point

The CLI entry point is `namicode_cli:cli_main`, registered as the `nami` console script in `setup.py`:
```python
entry_points={
    "console_scripts": [
        "nami=namicode_cli:cli_main",
    ],
}
```

The main flow is: `__main__.py` → `main.py` (cli_main, run_cli_session) → `agent.py` (create_agent_with_config) → LangGraph execution

### Color Theme

The CLI uses a red & white color scheme configured in `config.py`:
- Primary: `#ef4444` (bright red)
- Secondary: `#dc2626` (deep red)
- Accent: `#fca5a5` (light red)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (orange)

### Contributing

When contributing to this project:
1. Ensure all tests pass: `make test`
2. Format code: `make format`
3. Check linting: `make lint`
4. Follow existing code style and conventions
5. Add type hints to new functions
6. Include docstrings (Google-style)
7. Update tests for new features

### Changelog Maintenance

After implementing new features, bug fixes, or significant changes:

1. Create/update a changelog file in the `changelog/` directory
2. Use versioning format: `changelog_v{version}.md` (e.g., `changelog_v0.1.md`)
3. Include for each change:
   - Date of change
   - Type: **Feature**, **Bug Fix**, **Refactor**, **Documentation**, etc.
   - Description of what changed
   - Related issue/PR number (if applicable)

Example entry:
```markdown
## v0.1.1 - 2025-01-15

### Features
- Added new MCP integration module for filesystem operations

### Bug Fixes
- Fixed session persistence crash when .nami directory doesn't exist

### Documentation
- Updated README with new installation instructions
```

**Changelog Directory:** `B:\Winter 2025 Projects\Nami-Code\Namicode-CodeAssistant-CLI\changelog\`

## Interactive CLI Commands

The CLI supports these commands during interactive sessions:

| Command | Description |
|---------|-------------|
| `/clear` | Clear screen and reset conversation |
| `/help` | Show help information |
| `/tokens` | Show token usage for current session |
| `/context` | Show detailed context window usage |
| `/compact <focus>` | Summarize conversation to free up context |
| `/init` | Explore codebase and create NAMI.MD file |
| `/mcp` | Manage MCP servers |
| `/model` | Switch between LLM providers |
| `/skills` | Manage skills (list, create) |
| `/agents` | Manage custom agents |
| `/sessions` | List and manage saved sessions |
| `/save` | Manually save current session |
| `/servers` | List and manage running dev servers |
| `/tests` | Run project tests |
| `/trace` | Manage LangSmith tracing |
| `/kill <pid\|name>` | Kill a running process |
| `/exit` | Exit the CLI |

### .gitignore Rule

**Critical**: Files listed in `.gitignore` should NEVER be read, scanned, edited, or accessed in any way. These files are excluded from version control for security, privacy, or practical reasons. Always respect this boundary.

---

## File Operations Best Practices

When working with files in this codebase, follow these patterns:

### Reading Files
- Always use pagination for large files (use `limit` and `offset` parameters)
- First scan: `read_file(path, limit=100)` to see file structure
- read_file specific sections: `read_file(path, offset=100, limit=200)`
- Only read full files when necessary for editing

### Writing Files
- Use `write_file` to create new files or overwrite existing ones
- Use `edit_file` for targeted modifications to preserve formatting
- Always use absolute paths starting with `/`

### Searching
- Use `glob` to find files by pattern (e.g., `**/*.py`)
- Use `grep` to search for text patterns across files
- Use pagination when searching large codebases

### Codebase Exploration Pattern
1. First scan: `read_file(path, limit=100)` - See structure
2. Targeted read: `read_file(path, offset=100, limit=200)` - Specific sections
3. Full read: Only when necessary for editing

## License

MIT License - see LICENSE file for details.