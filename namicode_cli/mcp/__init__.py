"""MCP (Model Context Protocol) integration for deepagents-cli."""

from namicode_cli.mcp.config import MCPConfig, MCPServerConfig
from namicode_cli.mcp.middleware import MCPMiddleware

__all__ = ["MCPConfig", "MCPServerConfig", "MCPMiddleware"]
