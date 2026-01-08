# Nami-Code Agentic Coding Tool Architecture

## Overview

Nami-Code CLI is an open-source terminal-based AI coding assistant built on the **Deep Agent** architecture pattern, inspired by Claude Code. It provides a rich CLI interface for AI-powered code assistance with built-in tools, customizable skills, persistent memory, and project awareness.

The CLI is built on top of the `deepagents` library (located in `deepagents-nami/`), which implements a **"Deep Agent"** architecture with four key components:
1. **Planning tool** (`write_todos`) for task management
2. **Sub-agents** (`task` tool) for parallel delegation and context isolation
3. **File system access** via multiple backends (local, sandbox)
4. **Detailed prompts** with memory and skills systems

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Core Framework | LangChain and LangGraph |
| Deep Agents | Custom `nami-deepagents` library |
| Terminal UI | Rich library |
| LLM Providers | OpenAI, Anthropic, Ollama, Google |
| Sandbox Providers | Modal, Runloop, Daytona, Docker |
| Extensibility | Model Context Protocol (MCP) |
| Package Manager | uv (recommended) |

---

## Project Structure

```
namicode-codeassistant-cli/
├── namicode_cli/                    # Main CLI package
│   ├── __init__.py                  # Package initialization
│   ├── __main__.py                  # Entry point
│   ├── main.py                      # CLI loop and argument parsing
│   ├── agent.py                     # Agent creation and configuration
│   ├── config.py                    # Settings, environment, constants
│   ├── execution.py                 # Task execution and streaming
│   ├── tools.py                     # Custom tool implementations
│   ├── ui.py                        # Rich-based UI rendering
│   ├── commands.py                  # Interactive command handlers
│   ├── input.py                     # Input handling (prompt_toolkit)
│   ├── model_manager.py             # LLM provider management
│   ├── agent_memory.py              # Agent memory middleware
│   ├── session_persistence.py       # Session save/restore
│   ├── session_restore.py           # Session restoration logic
│   ├── skills/                      # Skills system
│   │   ├── commands.py              # Skill management commands
│   │   ├── load.py                  # Skill loading logic
│   │   └── middleware.py            # Skills integration middleware
│   ├── mcp/                         # Model Context Protocol
│   │   ├── client.py                # MCP client implementation
│   │   ├── commands.py              # MCP management commands
│   │   ├── config.py                # MCP configuration
│   │   ├── middleware.py            # MCP integration middleware
│   │   └── presets.py               # Pre-configured MCP servers
│   ├── integrations/                # Sandbox providers
│   │   ├── sandbox_factory.py       # Sandbox backend factory
│   │   ├── modal.py                 # Modal sandbox
│   │   ├── runloop.py               # Runloop sandbox
│   │   ├── daytona.py               # Daytona sandbox
│   │   └── docker.py                # Docker sandbox
│   ├── errors/                      # Error handling
│   └── default_agent_prompt.md      # Default system prompt
├── deepagents-nami/                 # Core deepagents library
│   ├── nami_deepagents/
│   │   ├── graph.py                 # Main create_deep_agent() factory
│   │   ├── middleware/
│   │   │   ├── filesystem.py        # FilesystemMiddleware
│   │   │   ├── subagents.py         # SubAgentMiddleware
│   │   │   └── patch_tool_calls.py
│   │   └── backends/
│   │       ├── filesystem.py        # Filesystem storage
│   │       ├── state.py             # State storage
│   │       ├── store.py             # LangGraph Store backend
│   │       ├── sandbox.py           # Sandbox backend
│   │       ├── composite.py         # Composite backend
│   │       ├── protocol.py          # Backend protocols
│   │       └── utils.py             # Backend utilities
│   └── pyproject.toml               # Library configuration
├── tests/                           # Test suite
│   ├── unit_tests/
│   └── integration_tests/
├── docs/                            # Documentation
├── changelog/                       # Version history
└── pyproject.toml                   # Project configuration
```

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Nami-Code CLI                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Main CLI Loop                             │   │
│  │  (main.py: run_cli_session)                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│              ┌───────────────┼───────────────┐                     │
│              ▼               ▼               ▼                     │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐            │
│  │ Configuration │ │    Session    │ │   Sandbox     │            │
│  │   (config)    │ │  Persistence  │ │  Factory      │            │
│  └───────────────┘ └───────────────┘ └───────────────┘            │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              LangGraph Deep Agent (Pregel)                   │   │
│  │                                                             │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │                   Middleware Stack                   │   │   │
│  │  │                                                     │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     AgentMemoryMiddleware                    │  │   │   │
│  │  │  │     (Loads agent.md, project memory)         │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     SkillsMiddleware                         │  │   │   │
│  │  │  │     (Progressive disclosure skills)          │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     MCPMiddleware                            │  │   │   │
│  │  │  │     (MCP server tools)                       │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     TodoListMiddleware                       │  │   │   │
│  │  │  │     (write_todos planning tool)              │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     SubAgentMiddleware                       │  │   │   │
│  │  │  │     (task tool for subagent delegation)      │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     FilesystemMiddleware                     │  │   │   │
│  │  │  │     (ls, read_file, write_file, glob, grep)  │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     HumanInTheLoopMiddleware                 │  │   │   │
│  │  │  │     (Tool approval UI)                       │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │     SummarizationMiddleware                  │  │   │   │
│  │  │  │     (Context window management)              │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  │                                                     │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │                           │                                  │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              LLM Model (Anthropic/OpenAI/etc)       │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│              ┌───────────────┼───────────────┐                     │
│              ▼               ▼               ▼                     │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐            │
│  │ CompositeBackend │ │  InMemoryStore │ │   Checkpoint   │          │
│  │ (Filesystem +    │ │  (Conversation │ │   (Messages)   │          │
│  │  Sandbox)        │ │   Memory)      │ │                │          │
│  └───────────────┘ └───────────────┘ └───────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. CLI Entry Point (`main.py`)

The `main.py` module serves as the primary CLI interface:

**Key Functions:**
- `parse_args()` - Parses command-line arguments
- `cli_main()` - Main entry point for the CLI
- `run_cli_session()` - Executes the interactive CLI loop
- `handle_command()` - Handles special CLI commands (/help, /tokens, etc.)

**CLI Arguments:**
| Flag | Description |
|------|-------------|
| `--agent` | Agent identifier (default: nami-agent) |
| `--auto-approve` | Auto-approve tool usage |
| `--sandbox` | Sandbox type (none, modal, daytona, runloop, docker) |
| `--sandbox-id` | Reuse existing sandbox |
| `--sandbox-setup` | Setup script path |
| `--no-splash` | Disable startup banner |
| `--continue` | Continue last session |
| `--version` | Show version |

**Interactive Commands:**
| Command | Description |
|---------|-------------|
| `/clear` | Clear screen and reset conversation |
| `/help` | Show help information |
| `/tokens` | Show token usage for current session |
| `/context` | Show detailed context window usage |
| `/compact` | Summarize conversation to free up context |
| `/init` | Explore codebase and create NAMI.MD file |
| `/mcp` | Manage MCP servers |
| `/model` | Switch between LLM providers |
| `/skills` | Manage skills |
| `/agents` | Manage custom agents |
| `/sessions` | List and manage saved sessions |
| `/save` | Manually save current session |
| `/servers` | List and manage running dev servers |
| `/tests` | Run project tests |
| `/trace` | Manage LangSmith tracing |
| `/kill` | Kill a running process |
| `/exit` | Exit the CLI |

### 2. Agent Creation (`agent.py`)

The `agent.py` module handles agent creation and configuration:

**Key Functions:**

| Function | Description |
|----------|-------------|
| `create_agent_with_config()` | Create a fully configured deep agent |
| `list_agents()` | Display available agent profiles |
| `reset_agent()` | Reset an agent to default configuration |
| `get_system_prompt()` | Build the base system prompt |

**Agent Configuration:**

```python
create_agent_with_config(
    model: BaseChatModel,
    assistant_id: str,
    tools: list[BaseTool],
    sandbox: SandboxBackendProtocol | None = None,
    sandbox_type: str | None = None
) -> tuple[Pregel, CompositeBackend]
```

**Tool Approval Configuration:**

The agent uses `HumanInTheLoopMiddleware` with custom descriptions for:
- `write_file` - File creation/overwrite
- `edit_file` - File modifications
- `web_search` - Web queries
- `fetch_url` - URL fetching
- `task` - Subagent delegation
- `run_tests` - Test execution
- `start_dev_server` - Development server startup

### 3. Configuration (`config.py`)

Centralized configuration management:

**Color Scheme (Red & White Theme):**
```python
COLORS = {
    "primary": "#ef4444",     # Bright red
    "secondary": "#dc2626",   # Deep red
    "accent": "#fca5a5",      # Light red
    "dim": "#9ca3af",         # Gray
    "user": "#ffffff",        # White
    "agent": "#ef4444",       # Bright red
    "success": "#10b981",     # Green
    "warning": "#f59e0b",     # Orange
}
```

**Supported LLM Providers:**
- **OpenAI** - Requires `OPENAI_API_KEY`
- **Anthropic** - Requires `ANTHROPIC_API_KEY`
- **Ollama** - Local models, requires `OLLAMA_BASE_URL`
- **Google** - Requires `GOOGLE_API_KEY`

**Project Detection:**
- Searches for `.git` directory to identify project root
- Supports `.claude/CLAUDE.md` and `.nami/NAMI.md` for project memory

**Settings Class:**
```python
@dataclass
class Settings:
    openai_api_key: str | None
    anthropic_api_key: str | None
    google_api_key: str | None
    tavily_api_key: str | None
    langsmith_api_key: str | None
    ollama_host: str | None
    project_root: Path | None
    langsmith_tracing_enabled: bool
```

### 4. Deep Agents Library (`deepagents-nami/`)

The core library that powers the CLI:

**Main Factory (`graph.py`):**

```python
create_deep_agent(
    model: BaseChatModel | None = None,
    tools: Sequence[BaseTool] | None = None,
    system_prompt: str | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: list[SubAgent] | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
) -> CompiledStateGraph
```

**Default Middleware Stack:**
1. `TodoListMiddleware` - Planning with `write_todos`
2. `FilesystemMiddleware` - File operations
3. `SubAgentMiddleware` - Task delegation
4. `SummarizationMiddleware` - Context management
5. `AnthropicPromptCachingMiddleware` - Token optimization
6. `PatchToolCallsMiddleware` - Tool call patching
7. `HumanInTheLoopMiddleware` - Tool approval (optional)

### 5. Middleware System

#### Agent Memory Middleware (`agent_memory.py`)

Loads long-term memory into the system prompt:

**Memory Sources (combined):**
1. `~/.nami/{agent}/agent.md` - User preferences (universal)
2. `{project}/.claude/CLAUDE.md` - Project context
3. `{project}/.nami/NAMI.md` - Nami project context
4. `{project}/NAMI.md` - Fallback project context

**State Schema:**
```python
class AgentMemoryState(AgentState):
    user_memory: str           # Personal preferences
    project_memory: str        # Project-specific context
```

#### Skills Middleware (`skills/middleware.py`)

Implements **progressive disclosure** of skills:

**Skills Directory Structure:**
```
~/.nami/{AGENT_NAME}/skills/
├── web-research/
│   ├── SKILL.md              # YAML frontmatter + instructions
│   └── helper.py             # Optional supporting files
└── code-review/
    └── SKILL.md

{project}/.nami/skills/
└── project-specific/
    └── SKILL.md
```

**Behavior:**
1. Load skill metadata (name, description) at session start
2. Inject skills list into system prompt
3. Agent reads full SKILL.md when relevant to a task
4. Project skills override user skills with same name

#### MCP Middleware (`mcp/middleware.py`)

Integrates Model Context Protocol servers:

**Features:**
- Loads MCP configurations from `~/.nami/mcp.json`
- Discovers tools from configured MCP servers
- Maintains persistent sessions for stateful servers
- Tools are namespaced by server: `servername__toolname`

**Configuration (`mcp/client.py`):**
```python
MCPConfig(
    servers={
        "server-name": {
            "command": ["python", "-m", "server"],
            "transport": "http|stdio",
            "url": "https://...",
        }
    }
)
```

#### Human-in-the-Loop Middleware

Built into LangChain agents, configurable via `interrupt_on`:

```python
interrupt_on = {
    "shell": {"allowed_decisions": ["approve", "reject"]},
    "write_file": {"allowed_decisions": ["approve", "reject"]},
    "edit_file": {"allowed_decisions": ["approve", "reject"]},
    "web_search": {"allowed_decisions": ["approve", "reject"]},
    "task": {"allowed_decisions": ["approve", "reject"]},
    # ...
}
```

### 6. Backend System

#### Backend Protocol (`deepagents-nami/backends/protocol.py`)

Defines interfaces for storage backends:

**BackendProtocol (base):**
```python
class BackendProtocol:
    def ls_info(path: str) -> list[dict]
    def read(path: str, offset=0, limit=0) -> str
    def write(path: str, content: str) -> WriteResult
    def edit(path: str, old_string: str, new_string: str) -> EditResult
    def glob(pattern: str) -> list[str]
    def grep(pattern: str, path: str | None, glob: str | None) -> list[dict]
```

**SandboxBackendProtocol (extends BackendProtocol):**
```python
class SandboxBackendProtocol(BackendProtocol):
    id: str                    # Sandbox identifier
    execute(command: str) -> dict  # Execute shell commands
```

#### Filesystem Backend (`deepagents-nami/backends/filesystem.py`)

Provides file operations for the agent:

**Tools Provided:**
| Tool | Description |
|------|-------------|
| `ls` | List files in a directory |
| `read_file` | Read file contents with pagination |
| `write_file` | Create or overwrite files |
| `edit_file` | Perform string replacements |
| `glob` | Find files by glob pattern |
| `grep` | Search for text patterns |

**Path Validation:**
- Virtual mode rejects Windows absolute paths (e.g., `C:/...`)
- Supports path prefix restrictions
- Prevents directory traversal attacks (`..`, `~`)

#### Composite Backend (`deepagents-nami/backends/composite.py`)

Combines multiple backends intelligently:
- Local filesystem backend
- Sandbox backend (remote execution)
- Fallback order based on operation type

### 7. Sandbox Integrations (`integrations/`)

| Provider | File | Features |
|----------|------|----------|
| **Modal** | `modal.py` | Cloud sandbox, persistent workspace |
| **Runloop** | `runloop.py` | Cloud development environment |
| **Daytona** | `daytona.py` | Containerized development |
| **Docker** | `docker.py` | Local container execution |

**Factory Pattern (`sandbox_factory.py`):**
```python
create_sandbox(
    sandbox_type: str,
    sandbox_id: str | None = None,
    setup_script_path: str | None = None,
) -> SandboxBackendProtocol
```

---

## Execution Flow

### 1. CLI Startup

```
cli_main()
  ├── parse_args()
  ├── check_cli_dependencies()
  ├── create_model() → LLM provider selection
  ├── create_sandbox() → Optional sandbox backend
  ├── create_agent_with_config() → Build LangGraph agent
  └── run_cli_session() → Enter interactive loop
```

### 2. Agent Initialization

```
create_agent_with_config()
  ├── Setup InMemoryStore for conversations
  ├── Configure LangSmith tracing (if enabled)
  ├── Create CompositeBackend (filesystem + sandbox)
  ├── Build middleware stack:
  │   ├── AgentMemoryMiddleware
  │   ├── SkillsMiddleware
  │   ├── MCPMiddleware
  │   ├── TodoListMiddleware
  │   ├── SubAgentMiddleware
  │   ├── FilesystemMiddleware
  │   ├── HumanInTheLoopMiddleware
  │   └── SummarizationMiddleware
  ├── Register custom tools:
  │   ├── web_search
  │   ├── fetch_url
  │   ├── http_request
  │   ├── run_tests
  │   ├── start_dev_server
  │   └── stop_server
  └── Return (graph, backend) tuple
```

### 3. Interactive Session Loop

```
run_cli_session()
  ├── Check path approval
  ├── Display startup banner
  ├── Create prompt session (prompt_toolkit)
  ├── Initialize token tracker
  ├── Enter message loop:
  │   ├── Get user input
  │   ├── Handle special commands (/help, /tokens, etc.)
  │   └── execute_task() → Stream agent response
  └── Auto-save sessions every 5 minutes
```

### 4. Task Execution (`execution.py`)

```
execute_task()
  ├── Stream agent responses
  ├── Process tool calls:
  │   ├── Check if approval required
  │   ├── If approval needed: prompt_for_tool_approval()
  │   └── Execute tool and render results
  ├── Track token usage
  └── Handle errors with ErrorHandler
```

### 5. Subagent Delegation

```
task tool invoked
  └── SubAgentMiddleware.handle_tool_call()
      ├── Create ephemeral subagent
      ├── Pass description as system prompt
      ├── Subagent operates with isolated context
      └── Return result to main agent
```

---

## Session Persistence

**Auto-Save Configuration:**
- Interval: 300 seconds (5 minutes)
- Message threshold: 5 new messages

**Session State:**
```python
class SessionState:
    thread_id: str
    session_id: str
    auto_approve: bool
    todos: list[dict]
```

**Persistence Flow:**
1. Session auto-saves on interval/message threshold
2. Sessions stored in: `~/.nami/sessions/`
3. Can be restored with `--continue` flag

---

## Memory System

### User Memory (`~/.nami/{agent}/agent.md`)

Stores **universal preferences** that apply across all projects:
- Communication style and tone
- General coding preferences
- Tool usage patterns
- Personal workflow habits

### Project Memory (`{project}/.nami/NAMI.md` or `.claude/CLAUDE.md`)

Stores **project-specific context**:
- Architecture and design patterns
- Coding conventions
- Project structure
- Testing strategies
- Team guidelines

**Loading Priority:**
1. `.claude/CLAUDE.md` (Claude Code primary)
2. `CLAUDE.md` (Claude Code fallback)
3. `.nami/NAMI.md` (Nami primary)
4. `NAMI.md` (Nami fallback)

All found files are combined, not replaced.

---

## Tool System

### Built-in Tools

| Tool | Module | Description |
|------|--------|-------------|
| `ls` | FilesystemMiddleware | List directory contents |
| `read_file` | FilesystemMiddleware | read_file file with pagination |
| `write_file` | FilesystemMiddleware | write_file/create files |
| `edit_file` | FilesystemMiddleware | Edit file contents |
| `glob` | FilesystemMiddleware | Find files by pattern |
| `grep` | FilesystemMiddleware | Search text in files |
| `execute` | FilesystemMiddleware | Run shell commands (sandbox) |
| `shell` | ShellMiddleware | Local shell execution |
| `web_search` | tools.py | Web search via Tavily |
| `fetch_url` | tools.py | Fetch web pages |
| `http_request` | tools.py | HTTP API requests |
| `write_todos` | TodoListMiddleware | Task planning |
| `task` | SubAgentMiddleware | Subagent delegation |
| `run_tests` | test_runner.py | Run test suites |
| `start_dev_server` | dev_server.py | Start dev servers |
| `stop_server` | dev_server.py | Stop dev servers |

### Tool Approval Workflow

```
Tool call invoked
  └── HumanInTheLoopMiddleware.check()
      ├── Check if tool requires approval
      └── If required:
          ├── Format tool description
          ├── Display approval prompt
          ├── Wait for user decision
          └── Return decision (approve/reject)
```

---

## Skills System

Skills provide specialized capabilities with **progressive disclosure**:

1. **Discovery Phase**: Agent knows skill name and description
2. **Activation Phase**: Agent reads SKILL.md when relevant
3. **Execution Phase**: Agent uses skill instructions and helper scripts

**Example Skill Structure:**
```yaml
# SKILL.md frontmatter
name: web-research
description: Structured web research workflow
---
# Skill instructions
## When to Use
...

## Workflow
1. Search for information
2. Organize findings
3. Synthesize results
```

---

## MCP Integration

**Architecture:**
```
MCPMiddleware
├── MCPConfig (loads mcp.json)
├── MultiServerMCPClient (connection management)
└── langchain-mcp-adapters (tool integration)
```

**Supported Transports:**
- `stdio` - Standard I/O communication
- `http` - HTTP-based MCP servers

**Tool Naming:**
- MCP tools are namespaced: `servername__toolname`
- Example: `docs-langchain__search`

---

## Tracing and Observability

**LangSmith Integration:**
```python
configure_tracing(
    api_key: str,
    project: str = "Nami-Code",
    workspace_id: str | None = None,
)
```

**Features:**
- Trace agent execution steps
- Monitor token usage
- Debug tool calls
- Performance analysis

---

## Error Handling

**Error Taxonomy (`errors/`):**
- `ToolExecutionError` - Tool execution failures
- `SandboxError` - Sandbox-related errors
- `ConfigurationError` - Configuration issues
- `SessionError` - Session management errors

**Error Handler Flow:**
```
Error occurs
  └── ErrorHandler.construct_error_response()
      ├── Classify error type
      ├── Format helpful message
      ├── Provide recovery suggestions
      └── Return structured error
```

---

## Code Quality

### Code Style
- **Formatter**: Ruff (line length: 100)
- **Type Checking**: MyPy strict mode
- **Docstrings**: Google-style (pydocstyle)

### Testing
- **Framework**: pytest
- **Test Structure**: `tests/unit_tests/`, `tests/integration_tests/`
- **Mocking**: Mock external dependencies (LLM APIs, sandboxes)

---

## Entry Points

| File | Purpose |
|------|---------|
| `__main__.py` | Package entry point |
| `setup.py` | Console script registration (`nami` command) |
| `main.py:cli_main()` | Main CLI function |

---

## Future Architecture Considerations

1. **Enhanced MCP Support**: More transport types, better error handling
2. **Multi-Model Routing**: Dynamic model selection based on task complexity
3. **Persistent Sandboxes**: Reusable sandbox environments across sessions
4. **Plugin System**: Third-party extension support
5. **Team Collaboration**: Shared memory and context across team members