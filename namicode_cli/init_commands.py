"""Initialization commands for creating .nami or .claude configurations."""

from pathlib import Path

from namicode_cli.config import COLORS, console


def init_project_config(style: str = "deepagents", scope: str = "project") -> None:
    """Initialize project or global configuration.

    Args:
        style: 'deepagents' or 'claude' - which directory structure to use
        scope: 'project' or 'global' - where to create the configuration
    """
    if scope == "project":
        _init_project_local(style)
    else:
        _init_global_config(style)


def _init_project_local(style: str) -> None:
    """Initialize project-specific configuration."""
    cwd = Path.cwd()

    # Determine directory name
    dir_name = ".claude" if style == "claude" else ".nami"
    config_dir = cwd / dir_name

    # Check if already exists
    if config_dir.exists():
        console.print(
            f"[yellow]Configuration already exists at {config_dir}[/yellow]",
            style=COLORS["dim"],
        )
        return

    # Create structure
    config_dir.mkdir(exist_ok=True)
    (config_dir / "skills").mkdir(exist_ok=True)

    # Create config file
    config_file = "CLAUDE.md" if style == "claude" else "agent.md"
    config_path = config_dir / config_file

    template = f"""# Project Configuration

This file contains project-specific instructions for the AI agent.

## Project Context

Describe your project here:
- What is this project about?
- What technologies/frameworks are used?
- What coding standards should be followed?

## Coding Guidelines

- Coding style preferences
- Testing requirements
- Documentation standards

## Project-Specific Tools

Describe any project-specific workflows or tools.

---

📁 This is a **project-specific** configuration.
Location: {config_dir}/

To create skills for this project:
```bash
nami skills create <skill-name> --project
```

To use a different agent:
```bash
nami --agent <agent-name>
```
"""

    config_path.write_text(template)

    # Success message
    console.print(f"\n✅ Project configuration created!", style=f"bold {COLORS['primary']}")
    console.print(f"\n📁 Location: {config_dir}/", style=COLORS["dim"])
    console.print(f"📄 Config file: {config_path}", style=COLORS["dim"])
    console.print(f"📂 Skills directory: {config_dir / 'skills'}/", style=COLORS["dim"])

    console.print(f"\n🎯 Next steps:", style=f"bold {COLORS['primary']}")
    console.print(f"  1. Edit {config_path} to add project-specific instructions")
    console.print(f"  2. Create project skills: nami skills create <name> --project")
    console.print(f"  3. Run: nami")
    console.print()


def _init_global_config(style: str) -> None:
    """Initialize global configuration."""
    home = Path.home()

    # Determine directory name
    dir_name = ".claude" if style == "claude" else ".nami"
    config_dir = home / dir_name

    # Check if already exists
    if config_dir.exists():
        console.print(
            f"[yellow]Global configuration already exists at {config_dir}[/yellow]",
            style=COLORS["dim"],
        )
        return

    # Create structure
    config_dir.mkdir(exist_ok=True)
    (config_dir / "agents").mkdir(exist_ok=True)
    (config_dir / "agents" / "nami-agent").mkdir(exist_ok=True)
    (config_dir / "skills").mkdir(exist_ok=True)

    # Create default agent
    agent_file = config_dir / "agents" / "nami-agent" / "agent.md"

    template = """# Default Agent Configuration

This file contains your personal preferences and coding style that apply everywhere.

## Your Personality & Style

Describe how you want the agent to communicate:
- Concise and direct
- Explain complex concepts simply
- Ask clarifying questions when uncertain

## Universal Coding Preferences

- Programming languages you prefer
- Code formatting standards
- Comment style
- Testing philosophy

## Tool Usage Patterns

How you prefer the agent to use tools:
- When to use web search
- File reading preferences
- Error handling approach

## Memory & Learning

The agent will remember your preferences across all projects.

---

📁 This is your **global** configuration.
Location: ~/.nami/agents/nami-agent/

To switch agents:
```bash
nami --agent <agent-name>
```

To create a new agent:
```bash
nami create <agent-name>
```
"""

    agent_file.write_text(template)

    # Create config.json
    config_json = config_dir / "config.json"
    config_json.write_text("""{
  "default_agent": "nami-agent",
  "version": "1.0.0"
}
""")

    # Success message
    console.print(f"\n✅ Global configuration created!", style=f"bold {COLORS['primary']}")
    console.print(f"\n📁 Location: {config_dir}/", style=COLORS["dim"])
    console.print(f"📂 Agents: {config_dir / 'agents'}/", style=COLORS["dim"])
    console.print(f"📂 Skills: {config_dir / 'skills'}/", style=COLORS["dim"])

    console.print(f"\n🎯 Next steps:", style=f"bold {COLORS['primary']}")
    console.print(f"  1. Edit {agent_file} to set your preferences")
    console.print(f"  2. Create global skills: nami skills create <name>")
    console.print(f"  3. Create more agents: nami create <agent-name>")
    console.print()


def interactive_init() -> None:
    """Interactive initialization with user prompts."""
    from prompt_toolkit import prompt
    from prompt_toolkit.shortcuts import radiolist_dialog

    console.print("\n🚀 DeepAgents Configuration Setup", style=f"bold {COLORS['primary']}")
    console.print()

    # Ask scope
    console.print("Where do you want to create the configuration?", style=COLORS["primary"])
    console.print("  1. Project-specific (in current directory)")
    console.print("  2. Global (in home directory, applies everywhere)")
    console.print()

    scope_choice = prompt("Choose (1 or 2): ", default="1").strip()
    scope = "project" if scope_choice == "1" else "global"

    # Ask style
    console.print(f"\nWhich style do you prefer?", style=COLORS["primary"])
    console.print("  1. Nami (.nami/ directory)")
    console.print("  2. Claude Code (.claude/ directory)")
    console.print()

    style_choice = prompt("Choose (1 or 2): ", default="1").strip()
    style = "nami" if style_choice == "1" else "claude"

    # Confirm
    dir_name = ".claude" if style == "claude" else ".nami"
    location = Path.cwd() / dir_name if scope == "project" else Path.home() / dir_name

    console.print(f"\n📝 Summary:", style=f"bold {COLORS['primary']}")
    console.print(f"  Scope: {scope.upper()}")
    console.print(f"  Style: {style.upper()}")
    console.print(f"  Location: {location}")
    console.print()

    confirm = prompt("Create this configuration? (y/n): ", default="y").strip().lower()

    if confirm == "y":
        init_project_config(style=style, scope=scope)
    else:
        console.print("Cancelled.", style=COLORS["dim"])
