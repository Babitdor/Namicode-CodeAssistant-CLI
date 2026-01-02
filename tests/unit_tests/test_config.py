"""Tests for config module including project discovery utilities."""

from pathlib import Path

from namicode_cli.config import _find_project_agent_md, _find_project_root


class TestProjectRootDetection:
    """Test project root detection via .git directory."""

    def test_find_project_root_with_git(self, tmp_path: Path) -> None:
        """Test that project root is found when .git directory exists."""
        # Create a mock project structure
        project_root = tmp_path / "my-project"
        project_root.mkdir()
        git_dir = project_root / ".git"
        git_dir.mkdir()

        # Create a subdirectory to search from
        subdir = project_root / "src" / "components"
        subdir.mkdir(parents=True)

        # Should find project root from subdirectory
        result = _find_project_root(subdir)
        assert result == project_root

    def test_find_project_root_no_git(self, tmp_path: Path) -> None:
        """Test that None is returned when no .git directory exists."""
        # Create directory without .git
        no_git_dir = tmp_path / "no-git"
        no_git_dir.mkdir()

        result = _find_project_root(no_git_dir)
        assert result is None

    def test_find_project_root_nested_git(self, tmp_path: Path) -> None:
        """Test that nearest .git directory is found (not parent repos)."""
        # Create nested git repos
        outer_repo = tmp_path / "outer"
        outer_repo.mkdir()
        (outer_repo / ".git").mkdir()

        inner_repo = outer_repo / "inner"
        inner_repo.mkdir()
        (inner_repo / ".git").mkdir()

        # Should find inner repo, not outer
        result = _find_project_root(inner_repo)
        assert result == inner_repo


class TestProjectAgentMdFinding:
    """Test finding project-specific agent.md files."""

    def test_find_agent_md_in_nami_dir(self, tmp_path: Path) -> None:
        """Test finding agent.md in .nami/ directory."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create .nami/agent.md
        nami_dir = project_root / ".nami"
        nami_dir.mkdir()
        agent_md = nami_dir / "agent.md"
        agent_md.write_text("Project instructions")

        result = _find_project_agent_md(project_root)
        assert len(result) == 1
        assert result[0] == agent_md

    def test_find_agent_md_in_root(self, tmp_path: Path) -> None:
        """Test finding agent.md in project root (fallback)."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create root-level agent.md (no .deepagents/)
        agent_md = project_root / "agent.md"
        agent_md.write_text("Project instructions")

        result = _find_project_agent_md(project_root)
        assert len(result) == 1
        assert result[0] == agent_md

    def test_both_agent_md_files_combined(self, tmp_path: Path) -> None:
        """Test that both agent.md files are returned when both exist."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create both locations
        nami_dir = project_root / ".nami"
        nami_dir.mkdir()
        nami_md = nami_dir / "agent.md"
        nami_md.write_text("In .nami/")

        root_md = project_root / "agent.md"
        root_md.write_text("In root")

        # Should return both, with .nami/ first
        result = _find_project_agent_md(project_root)
        assert len(result) == 2
        assert result[0] == nami_md
        assert result[1] == root_md

    def test_find_agent_md_not_found(self, tmp_path: Path) -> None:
        """Test that empty list is returned when no agent.md exists."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = _find_project_agent_md(project_root)
        assert result == []

    def test_find_nami_md_in_root(self, tmp_path: Path) -> None:
        """Test finding NAMI.md in project root (created by /init command)."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create root-level NAMI.md
        nami_md = project_root / "NAMI.md"
        nami_md.write_text("# Project Documentation")

        result = _find_project_agent_md(project_root)
        assert len(result) == 1
        assert result[0] == nami_md

    def test_find_claude_md_in_claude_dir(self, tmp_path: Path) -> None:
        """Test finding CLAUDE.md in .claude/ directory."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create .claude/CLAUDE.md
        claude_dir = project_root / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("Claude Code instructions")

        result = _find_project_agent_md(project_root)
        assert len(result) == 1
        assert result[0] == claude_md

    def test_all_config_files_combined(self, tmp_path: Path) -> None:
        """Test that all config files are returned in priority order."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create all possible locations
        claude_dir = project_root / ".claude"
        claude_dir.mkdir()
        claude_dir_md = claude_dir / "CLAUDE.md"
        claude_dir_md.write_text("In .claude/")

        nami_dir = project_root / ".nami"
        nami_dir.mkdir()
        nami_dir_md = nami_dir / "agent.md"
        nami_dir_md.write_text("In .nami/")

        root_claude_md = project_root / "CLAUDE.md"
        root_claude_md.write_text("Root CLAUDE.md")

        root_nami_md = project_root / "NAMI.md"
        root_nami_md.write_text("Root NAMI.md")

        root_agent_md = project_root / "agent.md"
        root_agent_md.write_text("Root agent.md")

        # Should return all in priority order
        result = _find_project_agent_md(project_root)
        assert len(result) == 5
        assert result[0] == claude_dir_md      # Priority 1
        assert result[1] == nami_dir_md        # Priority 2
        assert result[2] == root_claude_md     # Priority 3
        assert result[3] == root_nami_md       # Priority 4
        assert result[4] == root_agent_md      # Priority 5
