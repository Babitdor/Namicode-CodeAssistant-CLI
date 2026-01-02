"""Middleware for integrating MCP servers with the agent.

This middleware loads MCP server configurations, discovers their tools,
and makes them available to the agent as callable functions.
"""

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, NotRequired, TypedDict

from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import StructuredTool
from langgraph.runtime import Runtime

from namicode_cli.mcp.client import MCPClient
from namicode_cli.mcp.config import MCPConfig


class MCPState(AgentState):
    """State for the MCP middleware."""

    mcp_tools: NotRequired[list[dict[str, Any]]]
    """List of MCP tools metadata (name, description, server)."""


class MCPStateUpdate(TypedDict):
    """State update for the MCP middleware."""

    mcp_tools: list[dict[str, Any]]
    """List of MCP tools metadata."""


MCP_SYSTEM_PROMPT = """

## MCP (Model Context Protocol) Tools Available

You have access to external tools provided by MCP servers. These extend your capabilities beyond built-in tools.

**Connected MCP Servers:**

{servers_list}

**How to Use MCP Tools:**

1. **Tool Naming**: MCP tools are namespaced by server name
   - Format: `servername__toolname`
   - Example: `docs-langchain__search` calls the `search` tool from the `docs-langchain` server

2. **Discovery**: All available MCP tools are listed above with their descriptions
   - Check the tool descriptions to understand what each tool does
   - Review the input schema if you need to know what parameters are required

3. **Invocation**: Call MCP tools exactly like built-in tools
   - The middleware automatically routes calls to the appropriate MCP server
   - You don't need to manage connections or authentication
   - Results are returned just like any other tool call

**When to Use MCP Tools:**

- **Domain-Specific Knowledge**: When you need specialized information (e.g., documentation search, API lookups)
- **External Data Access**: When the task requires data from external systems or databases
- **Specialized Capabilities**: When MCP tools offer functionality not available in built-in tools
- **User's Domain**: When the user's request clearly maps to an MCP server's domain (check descriptions above)

**Best Practices:**

- Read tool descriptions carefully to understand capabilities and limitations
- Prefer MCP tools when they're specifically designed for the task
- Combine MCP tools with built-in tools for comprehensive solutions
- If an MCP tool fails, explain the error and try alternative approaches

**Important Notes:**

- MCP servers may become unavailable - handle tool call failures gracefully
- Some tools may have rate limits or require specific permissions
- Tool availability is shown above - only use tools that are currently listed

Remember: MCP tools are powerful extensions that give you access to specialized knowledge and capabilities. Use them when they match the user's needs!
"""


class MCPMiddleware(AgentMiddleware):
    """Middleware for integrating MCP servers with the agent.

    This middleware:
    - Loads MCP server configurations from ~/.nami/mcp.json
    - Discovers tools from configured MCP servers
    - Registers MCP tools with the agent
    - Handles tool calls by routing them to the appropriate MCP server

    Args:
        config_path: Optional path to mcp.json config file
    """

    state_schema = MCPState

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the MCP middleware.

        Args:
            config_path: Optional path to mcp.json config file.
                       Defaults to ~/.nami/mcp.json
        """
        self.mcp_config = MCPConfig(config_path)
        self.clients: dict[str, MCPClient] = {}
        self._tools_cache: list[dict[str, Any]] = []

    async def on_session_start(
        self,
        runtime: Runtime,
        *,
        state: MCPState,
    ) -> MCPStateUpdate | None:
        """Initialize MCP servers and discover tools at session start.

        Args:
            runtime: The LangGraph runtime instance
            state: Current agent state

        Returns:
            State update with MCP tools metadata, or None if no servers configured
        """
        # Load MCP server configurations
        servers = self.mcp_config.list_servers()

        if not servers:
            # No MCP servers configured
            return None

        # Initialize clients and discover tools
        tools_metadata = []
        for name, config in servers.items():
            try:
                client = MCPClient(name, config)
                self.clients[name] = client

                # Discover tools from this server
                tools = await client.list_tools()

                for tool in tools:
                    tools_metadata.append({
                        "name": tool["name"],
                        "description": tool["description"],
                        "server": name,
                        "inputSchema": tool["inputSchema"],
                    })

            except Exception as e:
                # Log error but continue with other servers
                print(f"Warning: Failed to connect to MCP server '{name}': {e}")
                continue

        self._tools_cache = tools_metadata

        # Inject MCP system prompt
        servers_list = self._format_servers_list(servers, tools_metadata)
        mcp_prompt = MCP_SYSTEM_PROMPT.format(servers_list=servers_list)

        # Append to system prompt
        if "system_messages" in state:
            state["system_messages"].append(mcp_prompt)
        else:
            # Fallback: add to state for later injection
            state["mcp_system_prompt"] = mcp_prompt  # type: ignore[typeddict-item]

        return {"mcp_tools": tools_metadata}

    def _format_servers_list(
        self,
        servers: dict[str, Any],
        tools_metadata: list[dict[str, Any]],
    ) -> str:
        """Format MCP servers and their tools for display in system prompt.

        Args:
            servers: Dictionary of server configurations
            tools_metadata: List of tool metadata

        Returns:
            Formatted string for system prompt
        """
        lines = []

        for name, config in servers.items():
            lines.append(f"\n**{name}** ({config.transport})")

            if config.description:
                lines.append(f"  {config.description}")

            # List tools from this server
            server_tools = [t for t in tools_metadata if t["server"] == name]

            if server_tools:
                lines.append(f"  Tools ({len(server_tools)}):")
                for tool in server_tools:
                    lines.append(
                        f"    - {tool['name']}: {tool['description']}"
                    )
            else:
                lines.append("  (No tools available)")

            lines.append("")

        return "\n".join(lines)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject MCP information into the system prompt.

        This runs on every model call to ensure MCP tools info is always available.

        Args:
            request: The model request being processed
            handler: The handler function to call with the modified request

        Returns:
            The model response from the handler
        """
        # Get MCP tools metadata from state
        mcp_tools = request.state.get("mcp_tools", [])

        if not mcp_tools:
            # No MCP tools available, skip injection
            return handler(request)

        # Get servers configuration
        servers = self.mcp_config.list_servers()

        # Format the MCP section
        servers_list = self._format_servers_list(servers, mcp_tools)
        mcp_section = MCP_SYSTEM_PROMPT.format(servers_list=servers_list)

        # Inject into system prompt
        if request.system_prompt:
            system_prompt = request.system_prompt + "\n\n" + mcp_section
        else:
            system_prompt = mcp_section

        return handler(request.override(system_prompt=system_prompt))

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """(async) Inject MCP information into the system prompt.

        Args:
            request: The model request being processed
            handler: The handler function to call with the modified request

        Returns:
            The model response from the handler
        """
        # Get MCP tools metadata from state
        mcp_tools = request.state.get("mcp_tools", [])

        if not mcp_tools:
            # No MCP tools available, skip injection
            return await handler(request)

        # Get servers configuration
        servers = self.mcp_config.list_servers()

        # Format the MCP section
        servers_list = self._format_servers_list(servers, mcp_tools)
        mcp_section = MCP_SYSTEM_PROMPT.format(servers_list=servers_list)

        # Inject into system prompt
        if request.system_prompt:
            system_prompt = request.system_prompt + "\n\n" + mcp_section
        else:
            system_prompt = mcp_section

        return await handler(request.override(system_prompt=system_prompt))

    def _create_mcp_tool_caller(
        self, server_name: str, tool_name: str
    ) -> Callable[..., Any]:
        """Create a callable function for an MCP tool.

        This factory method properly captures server_name and tool_name
        in a closure, avoiding the closure-in-loop bug.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool on that server

        Returns:
            Async callable that invokes the MCP tool
        """

        async def call_mcp_tool(**kwargs: Any) -> Any:
            """Call an MCP tool.

            Args:
                **kwargs: Tool arguments

            Returns:
                Tool execution result
            """
            client = self.clients.get(server_name)
            if not client:
                msg = f"MCP server '{server_name}' not found"
                raise ValueError(msg)

            result = await client.call_tool(tool_name, arguments=kwargs)
            return result

        return call_mcp_tool

    def create_mcp_tools(self) -> list[StructuredTool]:
        """Create LangChain tools from MCP tools metadata.

        Returns:
            List of StructuredTool instances that wrap MCP tool calls
        """
        tools = []

        for tool_meta in self._tools_cache:
            server_name = tool_meta["server"]
            tool_name = tool_meta["name"]

            # Use factory method to properly capture server_name and tool_name
            call_mcp_tool = self._create_mcp_tool_caller(server_name, tool_name)

            # Create StructuredTool
            structured_tool = StructuredTool.from_function(
                func=call_mcp_tool,
                name=f"{server_name}__{tool_name}",
                description=tool_meta["description"],
                args_schema=tool_meta.get("inputSchema"),
            )

            tools.append(structured_tool)

        return tools


__all__ = ["MCPMiddleware"]
