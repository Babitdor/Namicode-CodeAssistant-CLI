"""MCP client for connecting to and managing MCP servers.

This module provides functionality to connect to MCP servers via different
transports (HTTP, stdio) and interact with their tools.
"""

import subprocess
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from namicode_cli.mcp.config import MCPServerConfig


class MCPClient:
    """Client for connecting to MCP servers."""

    def __init__(self, name: str, config: MCPServerConfig) -> None:
        """Initialize MCP client.

        Args:
            name: Server name/identifier
            config: Server configuration
        """
        self.name = name
        self.config = config
        self._session: ClientSession | None = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[ClientSession]:
        """Connect to the MCP server and yield a session.

        Yields:
            ClientSession instance for interacting with the server

        Raises:
            ValueError: If transport type is not supported
            RuntimeError: If connection fails
        """
        if self.config.transport == "stdio":
            if not self.config.command:
                msg = "stdio transport requires a command"
                raise ValueError(msg)

            async with self._connect_stdio() as session:
                yield session

        elif self.config.transport == "http":
            if not self.config.url:
                msg = "HTTP transport requires a URL"
                raise ValueError(msg)

            async with self._connect_http() as session:
                yield session

        else:
            msg = f"Unsupported transport type: {self.config.transport}"
            raise ValueError(msg)

    @asynccontextmanager
    async def _connect_stdio(self) -> AsyncIterator[ClientSession]:
        """Connect to MCP server via stdio transport.

        Yields:
            ClientSession instance

        Raises:
            RuntimeError: If connection fails
        """
        if not self.config.command:
            msg = "stdio transport requires a command"
            raise ValueError(msg)

        # Build server parameters
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args if self.config.args else [],
            env=self.config.env if self.config.env else None,
        )

        try:
            # Create stdio client
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    yield session

        except subprocess.SubprocessError as e:
            msg = f"Failed to start MCP server '{self.name}': {e}"
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Failed to connect to MCP server '{self.name}': {e}"
            raise RuntimeError(msg) from e

    @asynccontextmanager
    async def _connect_http(self) -> AsyncIterator[ClientSession]:
        """Connect to MCP server via HTTP/SSE transport.

        Uses Server-Sent Events (SSE) for communication with HTTP-based MCP servers.
        The URL should point to the SSE endpoint (typically /sse or /mcp).

        Yields:
            ClientSession instance

        Raises:
            RuntimeError: If connection fails
        """
        if not self.config.url:
            msg = "HTTP transport requires a URL"
            raise ValueError(msg)

        # Build headers from env config (can be used for auth tokens, etc.)
        headers: dict[str, Any] = {}
        if self.config.env:
            # Convention: env vars starting with HTTP_HEADER_ become headers
            for key, value in self.config.env.items():
                if key.startswith("HTTP_HEADER_"):
                    header_name = key[12:].replace("_", "-")  # HTTP_HEADER_X_API_KEY -> X-Api-Key
                    headers[header_name] = value

        try:
            # Create SSE client connection
            async with sse_client(
                url=self.config.url,
                headers=headers if headers else None,
                timeout=30.0,  # Connection timeout
                sse_read_timeout=300.0,  # Read timeout for SSE events
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    yield session

        except httpx.TimeoutException as e:
            msg = f"Connection to MCP server '{self.name}' timed out: {e}"
            raise RuntimeError(msg) from e
        except httpx.ConnectError as e:
            msg = f"Failed to connect to MCP server '{self.name}' at {self.config.url}: {e}"
            raise RuntimeError(msg) from e
        except httpx.HTTPStatusError as e:
            msg = f"HTTP error from MCP server '{self.name}': {e.response.status_code}"
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Failed to connect to MCP server '{self.name}': {e}"
            raise RuntimeError(msg) from e

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all tools available from this MCP server.

        Returns:
            List of tool definitions with name, description, and schema

        Raises:
            RuntimeError: If not connected or listing fails
        """
        async with self.connect() as session:
            try:
                result = await session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                        "inputSchema": tool.inputSchema,
                    }
                    for tool in result.tools
                ]
            except Exception as e:
                msg = f"Failed to list tools from server '{self.name}': {e}"
                raise RuntimeError(msg) from e

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            RuntimeError: If not connected or tool call fails
        """
        async with self.connect() as session:
            try:
                result = await session.call_tool(
                    tool_name,
                    arguments=arguments or {},
                )
                return result
            except Exception as e:
                msg = f"Failed to call tool '{tool_name}' on server '{self.name}': {e}"
                raise RuntimeError(msg) from e


async def check_server_connection(name: str, config: MCPServerConfig) -> tuple[bool, str]:
    """Check connection to an MCP server.

    This function tests whether a connection can be established to the given
    MCP server configuration.

    Args:
        name: Server name/identifier
        config: Server configuration

    Returns:
        Tuple of (success, message)
    """
    try:
        client = MCPClient(name, config)
        tools = await client.list_tools()
        return True, f"Connected successfully. Found {len(tools)} tools."
    except Exception as e:
        return False, f"Connection failed: {e}"


__all__ = ["MCPClient", "check_server_connection"]
