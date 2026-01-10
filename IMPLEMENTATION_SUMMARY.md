# Named Agents as Subagents Implementation Summary

## Overview

Successfully implemented the feature to pass all named agents from `~/.nami/agents/` and `.nami/agents/` as subagents to the core NAMI agent. These agents can now be invoked via the `task` tool.

## What Was Implemented

### 1. Agent Discovery and SubAgent Building (`namicode_cli/agent.py`)

**Added Functions:**
- `_extract_agent_description(agent_md_content: str) -> str`
  - Extracts a concise description from agent.md content
  - Used to populate the subagent description field

- `build_named_subagents(assistant_id: str, tools: list[BaseTool]) -> list[SubAgent]`
  - Discovers all agents from both global (`~/.nami/agents/`) and project (`.nami/agents/`) directories
  - Excludes the current main agent (specified by assistant_id)
  - Reads each agent's `agent.md` file and creates a SubAgent specification
  - Returns a list of SubAgent objects ready for SubAgentMiddleware

**Key Features:**
- Automatically discovers agents from both global and project scopes
- Skips agents without agent.md files (with warnings)
- Extracts meaningful descriptions from agent.md content
- Passes the same tools to each subagent as the main agent has

### 2. SubAgentMiddleware Integration (`namicode_cli/agent.py`)

**Modified Function:** `create_agent_with_config()`

**Changes:**
- Added import for `SubAgentMiddleware` and `SubAgent` from `nami_deepagents.middleware.subagents`
- Call `build_named_subagents()` to get all available named agents
- Create and configure `SubAgentMiddleware` with:
  - All named agents as custom subagents
  - General-purpose agent enabled (default)
  - Same model and tools as main agent
- Append SubAgentMiddleware to the middleware stack

**Integration Points:**
- Works for both local mode and sandbox mode
- Middleware is added after all other middleware (file tracker, agent memory, skills, MCP, shared memory, shell)

## How It Works

### Agent Discovery Flow

1. When `create_agent_with_config()` is called, it invokes `build_named_subagents()`
2. `build_named_subagents()` uses `settings.get_all_agents()` to find all agent directories
3. For each agent (excluding the main agent):
   - Reads the `agent.md` file
   - Extracts a description
   - Creates a SubAgent specification with:
     - `name`: The agent directory name
     - `description`: `[global/project] <extracted description>`
     - `system_prompt`: Full content of agent.md
     - `tools`: Same tools as main agent

### SubAgentMiddleware Behavior

The SubAgentMiddleware automatically:

1. **Creates a `task` tool** that lists all available subagent types
2. **Injects system prompt information** about:
   - All available subagent types and their descriptions
   - How to use the task tool
   - Best practices for delegating to subagents
   - Example usage patterns

3. **Provides examples** showing when to use custom agents vs general-purpose agent

### Example System Prompt Injection

When your named agents are loaded, the core agent receives information like:

```
## `task` (subagent spawner)

You have access to a `task` tool to launch short-lived subagents that handle isolated tasks.

Available agent types and the tools they have access to:
- general-purpose: General-purpose agent for researching complex questions, searching for files...
- code-reviewer: [global] You are an expert code reviewer dedicated to ensuring high software quality...
- nodejs-expert: [global] You are nodejs-expert, a specialized AI coding assistant focused exclusively on Node.js...
- Playwright: [global] You are an AI agent specializing in browser automation via Microsoft's Playwright...
- sysmlv2-agent: [global] You are sysmlv2-agent, an expert AI coding assistant specialized in Systems Modeling...
...

When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.
```

## Test Results

Successfully tested with 19 existing agents:
- Changelog-agent
- code-reviewer
- nami-agent
- nodejs-expert
- Playwright
- project-structure-agent
- Serena
- sysmlv2-agent
- ultra-mode-agent
- (+ 10 eval agents)

All agents were correctly:
- Discovered from `~/.nami/agents/`
- Loaded with their system prompts
- Made available as subagent types
- Listed in the task tool description

## Usage

### How to Invoke Named Agents

The core NAMI agent can now use the `task` tool to delegate work to named agents:

```python
# Example: Using the code-reviewer agent
task(
    description="Please review this Python function for best practices, security, and performance...",
    subagent_type="code-reviewer"
)

# Example: Using the nodejs-expert agent
task(
    description="Help me implement an Express.js middleware for rate limiting...",
    subagent_type="nodejs-expert"
)

# Example: Using the Playwright agent
task(
    description="Navigate to example.com and click the login button...",
    subagent_type="Playwright"
)
```

### Automatic Discovery

Named agents are automatically discovered when:
- They exist in `~/.nami/agents/<agent-name>/`
- Or in `.nami/agents/<agent-name>/` (project-specific)
- They have an `agent.md` file
- The agent name is different from the current main agent

### No Configuration Required

The implementation is fully automatic:
- No need to manually register agents
- No configuration files to edit
- Just create an agent directory with `agent.md` and it becomes available as a subagent

## Files Modified

1. **namicode_cli/agent.py**
   - Added imports for SubAgentMiddleware and SubAgent
   - Added `_extract_agent_description()` helper function
   - Added `build_named_subagents()` function
   - Modified `create_agent_with_config()` to integrate SubAgentMiddleware

## Benefits

1. **Automatic Discovery**: All named agents become available as subagents without manual configuration
2. **Same Capabilities**: Each subagent has access to the same tools as the main agent
3. **Specialized Expertise**: Named agents can have specialized system prompts for specific domains
4. **Context Isolation**: Using subagents keeps the main agent's context clean
5. **Parallel Execution**: Multiple named agents can work on different subtasks simultaneously
6. **Flexible**: Works for both global agents (shared across projects) and project-specific agents

## Next Steps

1. **Run Tests**: Use `make test` to ensure all tests pass
2. **Try It Out**: Start nami and use the task tool with one of your named agents
3. **Create New Agents**: Add more specialized agents to `~/.nami/agents/` for specific tasks
4. **Document Agent Purposes**: Update agent.md files with clear descriptions for better subagent selection

## Example Workflow

```bash
# List available agents
nami list

# Start nami
nami

# In the nami session, the agent can now use:
# task(description="Review my code for security issues", subagent_type="code-reviewer")
# task(description="Help me build a Node.js API", subagent_type="nodejs-expert")
# task(description="Automate browser testing", subagent_type="Playwright")
```

The core agent is now aware of all these specialized agents and can delegate appropriate tasks to them!
