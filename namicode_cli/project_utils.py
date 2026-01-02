"""Utilities for project root detection and project-specific configuration."""

from pathlib import Path


def find_project_root(start_path: Path | None = None) -> Path | None:
    """Find the project root by looking for .git directory or project markers.

    Walks up the directory tree from start_path (or cwd) looking for:
    1. .git directory (primary indicator)
    2. .claude/ directory (Claude Code project)
    3. .nami/ directory (DeepAgents project)
    4. CLAUDE.md file (Claude Code project marker)
    5. NAMI.md file (Nami project marker)

    Args:
        start_path: Directory to start searching from. Defaults to current working directory.

    Returns:
        Path to the project root if found, None otherwise.
    """
    current = Path(start_path or Path.cwd()).resolve()

    # Walk up the directory tree
    for parent in [current, *list(current.parents)]:
        # Check for .git directory (primary indicator)
        if (parent / ".git").exists():
            return parent

        # Check for .claude/ directory (Claude Code project)
        if (parent / ".claude").exists() and (parent / ".claude").is_dir():
            return parent

        # Check for .nami/ directory (DeepAgents project)
        if (parent / ".nami").exists() and (parent / ".nami").is_dir():
            return parent

        # Check for CLAUDE.md file (Claude Code project marker)
        if (parent / "CLAUDE.md").exists():
            return parent

        # Check for NAMI.md file (Nami project marker)
        if (parent / "NAMI.md").exists():
            return parent

    return None


def find_project_agent_md(project_root: Path) -> list[Path]:
    """Find project-specific agent.md, CLAUDE.md, and NAMI.md file(s).

    Checks multiple locations and returns ALL that exist (in priority order):
    1. project_root/.claude/CLAUDE.md (Claude Code primary)
    2. project_root/.nami/agent.md (DeepAgents primary)
    3. project_root/CLAUDE.md (Claude Code fallback)
    4. project_root/NAMI.md (Nami fallback - created by /init command)
    5. project_root/agent.md (DeepAgents fallback)

    All files found will be loaded and combined hierarchically.

    Args:
        project_root: Path to the project root directory.

    Returns:
        List of paths to project config files (may contain 0-5 paths).
    """
    paths = []

    # Priority 1: .claude/CLAUDE.md (Claude Code style)
    claude_dir_md = project_root / ".claude" / "CLAUDE.md"
    if claude_dir_md.exists():
        paths.append(claude_dir_md)

    # Priority 2: .nami/agent.md (DeepAgents style)
    deepagents_md = project_root / ".nami" / "agent.md"
    if deepagents_md.exists():
        paths.append(deepagents_md)

    # Priority 3: CLAUDE.md in root (Claude Code fallback)
    root_claude_md = project_root / "CLAUDE.md"
    if root_claude_md.exists():
        paths.append(root_claude_md)

    # Priority 4: NAMI.md in root (created by /init command)
    root_nami_md = project_root / "NAMI.md"
    if root_nami_md.exists():
        paths.append(root_nami_md)

    # Priority 5: agent.md in root (DeepAgents fallback)
    root_agent_md = project_root / "agent.md"
    if root_agent_md.exists():
        paths.append(root_agent_md)

    return paths


def get_project_config_dirs(project_root: Path) -> list[Path]:
    """Get all project configuration directories that exist.

    Returns both .claude/ and .nami/ directories if they exist.

    Args:
        project_root: Path to the project root directory.

    Returns:
        List of configuration directory paths that exist.
    """
    config_dirs = []

    claude_dir = project_root / ".claude"
    if claude_dir.exists() and claude_dir.is_dir():
        config_dirs.append(claude_dir)

    deepagents_dir = project_root / ".nami"
    if deepagents_dir.exists() and deepagents_dir.is_dir():
        config_dirs.append(deepagents_dir)

    return config_dirs


def find_project_skills(project_root: Path) -> list[Path]:
    """Find project-specific skills directories.

    Checks for skills in both .claude/ and .nami/ directories.

    Args:
        project_root: Path to the project root directory.

    Returns:
        List of skills directory paths that exist.
    """
    skills_dirs = []

    # Check .claude/skills/
    claude_skills = project_root / ".claude" / "skills"
    if claude_skills.exists() and claude_skills.is_dir():
        skills_dirs.append(claude_skills)

    # Check .nami/skills/
    deepagents_skills = project_root / ".nami" / "skills"
    if deepagents_skills.exists() and deepagents_skills.is_dir():
        skills_dirs.append(deepagents_skills)

    return skills_dirs
