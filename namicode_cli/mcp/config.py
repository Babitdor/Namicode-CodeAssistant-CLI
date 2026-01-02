"""MCP configuration management.

Handles loading, saving, and validating MCP server configurations.
Configuration is stored at ~/.nami/mcp.json in the following format:

{
  "mcpServers": {
    "server-name": {
      "transport": "http" | "stdio",
      "url": "https://...",  // for HTTP transport
      "command": "...",      // for stdio transport
      "args": [...],         // optional, for stdio transport
      "env": {...},          // optional environment variables
      "description": "..."   // optional description
    }
  }
}
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    transport: Literal["http", "stdio"]
    url: str | None = None
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    description: str | None = None

    @model_validator(mode="after")
    def validate_transport_requirements(self) -> "MCPServerConfig":
        """Validate that transport-specific requirements are met."""
        if self.transport == "http" and not self.url:
            msg = "HTTP transport requires a URL"
            raise ValueError(msg)
        if self.transport == "stdio" and not self.command:
            msg = "stdio transport requires a command"
            raise ValueError(msg)
        return self


class MCPConfig:
    """Manages MCP server configurations."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize MCP config.

        Args:
            config_path: Path to mcp.json config file. Defaults to ~/.nami/mcp.json
        """
        if config_path is None:
            config_path = Path.home() / ".nami" / "mcp.json"
        self.config_path = config_path
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, MCPServerConfig]:
        """Load MCP server configurations from disk.

        Returns:
            Dictionary mapping server names to configurations
        """
        if not self.config_path.exists():
            return {}

        try:
            with self.config_path.open() as f:
                data = json.load(f)

            servers = data.get("mcpServers", {})
            return {
                name: MCPServerConfig(**config) for name, config in servers.items()
            }
        except (json.JSONDecodeError, ValueError) as e:
            msg = f"Failed to load MCP config from {self.config_path}: {e}"
            raise RuntimeError(msg) from e

    def save(self, servers: dict[str, MCPServerConfig]) -> None:
        """Save MCP server configurations to disk.

        Args:
            servers: Dictionary mapping server names to configurations
        """
        data = {
            "mcpServers": {
                name: config.model_dump(exclude_none=True)
                for name, config in servers.items()
            }
        }

        with self.config_path.open("w") as f:
            json.dump(data, f, indent=2)

    def add_server(self, name: str, config: MCPServerConfig) -> None:
        """Add or update an MCP server configuration.

        Args:
            name: Server name/identifier
            config: Server configuration
        """
        servers = self.load()
        servers[name] = config
        self.save(servers)

    def remove_server(self, name: str) -> bool:
        """Remove an MCP server configuration.

        Args:
            name: Server name/identifier

        Returns:
            True if server was removed, False if not found
        """
        servers = self.load()
        if name not in servers:
            return False
        del servers[name]
        self.save(servers)
        return True

    def get_server(self, name: str) -> MCPServerConfig | None:
        """Get configuration for a specific server.

        Args:
            name: Server name/identifier

        Returns:
            Server configuration or None if not found
        """
        servers = self.load()
        return servers.get(name)

    def list_servers(self) -> dict[str, MCPServerConfig]:
        """List all configured MCP servers.

        Returns:
            Dictionary mapping server names to configurations
        """
        return self.load()
