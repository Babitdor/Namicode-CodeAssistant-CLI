## v0.0.11 - 2025-01-08

### Features

#### Image Loading Support (2d1a8cd)
- New `namicode_cli/image_utils.py` module (209 lines)
- Supports loading and displaying images in terminal
- Added dependencies for image processing
- Used for banner display and visual enhancements

#### Session File Tracking & /files Command (037644f)
- New `/files` command shows session file summary
- Tracks all read_file operations with timestamps, content hashes, line/character counts
- Maintains write history per file with operation types
- Provides `SessionFileTracker` dataclass for session-level tracking
- Supports file operation statistics and content previews

#### FileTrackerMiddleware - read_file-Before-edit Enforcement (037644f)
- **Hard read-before-edit enforcement**: Rejects edit operations on files that haven't been read in the current session
- **File content caching**: Stores file hashes and content for edit verification
- **Security enhancement**: Prevents accidental edits to files outside project scope
- Added `namicode_cli/file_tracker.py` with 572 lines of middleware implementation

#### Lower Context Summarization Thresholds (037644f)
- Triggers context summarization at 70% instead of previous threshold
- Reduces token usage before context overflow
- Improves long-running session performance

#### Agent Colors via YAML Frontmatter (477f392)
- Custom agents can define colors in `agent.md` YAML frontmatter:
  ```markdown
  ---
  color: #22c55e
  ---
  ```
- Added `parse_agent_color()`, `get_agent_color()`, `set_agent_color()` functions
- Color applies to spinner, agent name, and output display
- Stored in `_agent_colors` registry in `config.py`

#### Shared Memory System (477f392)
- Cross-agent memory sharing with attribution tracking
- New `namicode_cli/shared_memory.py` module (405 lines)
- Supports `write_memory`, `read_memory`, `list_memories`, `delete_memory` tools
- Memory entries include author attribution (`main-agent` or `subagent:<name>`)
- Timestamps and optional tags for each memory
- Module-level singleton via `get_shared_memory_middleware()`

#### Agent Memory Middleware (fdcd958, 477f392)
- Loads agent.md memory files at session start
- Supports both global (`~/.nami/agents/<name>/agent.md`) and project-level memory
- Automatic memory updates based on user feedback
- YAML frontmatter parsing for configuration

### UI/UX Improvements

#### Branded ASCII Art Update (2d1a8cd)
- Renamed `DEEP_AGENTS_ASCII` → `NAMI_CODE_ASCII` for proper branding
- Updated all references in `commands.py`, `ui.py`, `input.py`
- Consistent branding across the CLI

#### Interactive Command Improvements (2d1a8cd)
- Improved agent creation prompts with better formatting
- Added example agent types with clearer descriptions
- Enhanced user guidance for agent configuration

### Bug Fixes

#### MCP Tool Loading Fix (037644f, 477f392)
- Fixed `tool_name_prefix` parameter issue in `load_mcp_tools()`
- Resolved errors for MCP servers: playwright, github, netlify

#### Subagent Output Visibility (037644f)
- Fixed subagent output visibility during task execution
- Removed namespace filtering that was hiding subagent messages
- Added visual labels (`🤖 [general-purpose]:`) for agent type

### Technical Changes

#### New Module: ACP Server (fdcd958)
- Added `acp/` directory with AI Communication Protocol server
- `acp/deepagents_acp/server.py` - 655 line server implementation
- Tests for chat model and server functionality
- Pyproject configuration for AI protocols

#### New Module: Image Utilities (2d1a8cd)
- New `namicode_cli/image_utils.py` for image loading/display
- Terminal-compatible image rendering support

#### New Module: Evaluation Framework (fdcd958)
- Added `evaluation/` directory with Harbor backend
- `deepagents_harbor/backend.py` - 377 line evaluation backend
- `deepagents_harbor/tracing.py` - LangSmith integration
- `evaluation/scripts/analyze.py` - Analysis script (796 lines)
- `evaluation/scripts/harbor_langsmith.py` - LangSmith integration (501 lines)
- Terminal-bench-2 integration for benchmark testing

#### Configuration Updates (493104c, 477f392)
- Added `nest-asyncio` dependency for async support
- Updated MCP-related dependencies
- Added `wcmatch` pattern matching library
- Added image processing dependencies (2d1a8cd)

#### Memory System Architecture (fdcd958, 477f392)
- Added `InMemoryStore` singleton for agent/subagent communication
- `reset_shared_store()` for session reset
- LangGraph Store backend integration
- CompositeBackend for multi-backend routing

#### Gitignore Updates (73c52f6)
- Added `.serena/cache/` to gitignore
- Excludes Serena AI assistant cache files

### Documentation

#### NAMI.md Files (037644f)
- Added comprehensive `.nami/NAMI.md` file (574 lines)
- Added root-level `NAMI.md` file (536 lines)
- Covers project overview, architecture, workflows, best practices
- AI assistant guidance for working with the codebase

#### README Updates (176420e)
- Updated documentation
- Added project references and examples

#### EVALUATION.md Documentation (New)
- Added comprehensive `docs/EVALUATION.md` guide
- Complete setup instructions for Harbor evaluation framework
- LangSmith integration guide
- Troubleshooting section

### Files Changed Summary

| Commit | Files Changed | Lines Added/Removed | Description |
|--------|---------------|---------------------|-------------|
| 2d1a8cd | 9 files | +413/-34 | UI changes, NAMI branding, image utilities |
| 73c52f6 | 1 file | +4/-1 | .gitignore updates |
| 176420e | 3 files | +3/-1 | README changes |
| 037644f | 8 files | +1952/-35 | FileTrackerMiddleware, /files command, context thresholds |
| 28617c3 | 1 file | +1/-1 | README update |
| 477f392 | 14 files | +706/-37 | Agent colors, shared memory |
| 493104c | 1 file | +3/0 | pyproject.toml |
| fdcd958 | 26 files | +12569/-13 | ACP server, evaluation framework |
| **Total** | **63+ files** | **~15,650 lines** | |