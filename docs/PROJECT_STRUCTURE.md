# Project Structure - Nami-Code CLI

A terminal-based AI coding assistant built with a modular architecture for extensibility and maintainability.

## Directory Overview

```
Namicode-CodeAssistant-CLI/
├── .claude/                    # Claude Code compatible configuration
│   └── agents/
│       └── prompt-toolkit-ui-builder.md
├── .env                        # Environment variables (gitignored)
├── .env.template               # Environment template
├── .gitignore                  # Git ignore rules
├── .ruff_cache/                # Ruff linter cache
├── .serena/                    # Serena project configuration
├── .venv/                      # Python virtual environment
├── assets/                     # Static assets (images, etc.)
├── deepagents-nami/            # Custom deepagents dependency
├── namicode_cli/               # Main CLI package
├── namicode_cli.egg-info/      # Package metadata
├── tests/                      # Test suite
├── Streaming.md                # Streaming documentation
├── Subagents.md                # Subagents documentation
├── subagent_fix_suggestions.md # Suggestions for subagent fixes
├── Makefile                    # Build and test automation
├── pyproject.toml              # Project configuration
├── setup.py                    # Setup script
├── uv.lock                     # UV lock file
└── LICENSE                     # MIT License
```

## Main Package Structure (`namicode_cli/`)

```
namicode_cli/
├── __init__.py                 # Package initialization
├── __main__.py                 # Entry point for `python -m namicode_cli`
├── __pycache__/                # Python bytecode cache
├── py.typed                    # PEP 561 marker for type hints
├── agent.py                    # Agent creation and configuration
├── agent_memory.py             # Agent memory/persistence management
├── commands.py                 # CLI command definitions
├── compaction.py               # Memory/context compaction utilities
├── config.py                   # Settings and environment configuration
├── context_manager.py          # Context management for tool calls
├── default_agent_prompt.md     # Default agent system prompt
├── dev_server.py               # Development server utilities
├── errors/                     # Error handling module
│   ├── __init__.py
│   ├── handlers.py             # Error handlers
│   └── taxonomy.py             # Error taxonomy/classification
├── execution.py                # Task execution and streaming
├── file_ops.py                 # File operations (read, write, glob, grep)
├── init_commands.py            # Initialization commands
├── input.py                    # Input handling (keyboard, CLI)
├── integrations/               # Sandbox provider integrations
│   ├── __init__.py
│   ├── daytona.py              # Daytona sandbox integration
│   ├── docker.py               # Docker sandbox integration
│   ├── modal.py                # Modal sandbox integration
│   ├── runloop.py              # Runloop sandbox integration
│   └── sandbox_factory.py      # Factory for creating sandbox instances
├── main.py                     # CLI entry point and main loop
├── mcp/                        # Model Context Protocol integration
│   ├── __init__.py
│   ├── client.py               # MCP client implementation
│   ├── commands.py             # MCP CLI commands
│   ├── config.py               # MCP configuration
│   ├── middleware.py           # MCP middleware
│   └── presets.py              # MCP server presets
├── migrate.py                  # Migration utilities
├── model_manager.py            # LLM model management
├── nami_config.py              # Nami configuration
├── path_approval.py            # Path approval/security
├── process_manager.py          # Process management
├── project_utils.py            # Project utilities
├── session_persistence.py      # Session persistence
├── session_restore.py          # Session restoration
├── shell.py                    # Shell command execution
├── skills/                     # Skills system
│   ├── __init__.py
│   ├── commands.py             # Skills CLI commands
│   ├── load.py                 # Skills loader
│   └── middleware.py           # Skills middleware
├── test_runner.py              # Test runner utilities
├── token_utils.py              # Token counting utilities
├── tools.py                    # Custom tool implementations
└── ui.py                       # Rich-based UI rendering
```

## Test Suite Structure (`tests/`)

```
tests/
├── integration_tests/          # Integration tests
├── test_project_memory.py      # Project memory tests
└── unit_tests/                 # Unit tests
```

## Configuration Directories

### Global Configuration (`~/.nami/`)

```
~/.nami/
├── agents/
│   └── default/
│       └── agent.md            # Global agent memory
└── skills/                     # Global skills directory
```

### Project Configuration (in project root)

```
my-project/
├── .nami/
│   ├── NAMI.md                 # Project-specific instructions
│   └── skills/                 # Project-specific skills
└── .claude/                    # Claude Code compatible config
```

## Architecture Overview

### Core Components

1. **Agent Layer** (`agent.py`, `agent_memory.py`)
   - Agent creation and configuration
   - Persistent memory management
   - System prompt handling

2. **Execution Layer** (`execution.py`, `process_manager.py`)
   - Task execution
   - Streaming responses
   - Process management

3. **Tools Layer** (`tools.py`, `file_ops.py`, `shell.py`)
   - Built-in tools (ls, read_file, write_file, edit_file, glob, grep)
   - Shell command execution
   - Web search and URL fetching

4. **UI Layer** (`ui.py`, `input.py`)
   - Rich-based terminal UI
   - Input handling
   - Progress indicators

5. **Skills System** (`skills/`)
   - Progressive disclosure skill loading
   - Skill commands
   - Skill middleware

6. **MCP Integration** (`mcp/`)
   - MCP client implementation
   - Server configuration
   - Middleware for tool integration

7. **Sandbox Integrations** (`integrations/`)
   - Modal
   - Runloop
   - Daytona
   - Docker
   - Factory pattern for creating sandbox instances

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point and main loop |
| `agent.py` | Agent configuration and creation |
| `execution.py` | Task execution with streaming |
| `config.py` | Settings and environment vars |
| `tools.py` | Custom tool implementations |
| `ui.py` | Terminal UI rendering |
| `pyproject.toml` | Project metadata and dependencies |
| `Makefile` | Build automation |

## Dependencies

### Core Dependencies

- **deepagents-nami** - Custom deepagents library for agent architecture
- **anthropic** - Anthropic API client
- **aiofiles** - Async file operations
- **aiohttp** - Async HTTP client/server

### Development Dependencies

- **pytest** - Testing framework
- **ruff** - Linting and formatting
- **mypy** - Type checking

## Build & Test Commands

```bash
# Run unit tests
make test

# Run integration tests
make test_integration

# Format code
make format

# Run linter
make lint

# Run CLI during development
make run
```

## Entry Points

The CLI can be invoked in multiple ways:

```bash
nami                          # Standard entry
python -m namicode_cli        # Via Python module
```

## License

MIT License - see LICENSE file for details.