import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class MCPClientManager:
    def __init__(self, command: str, args: List[str]):
        # We'll create server_parameters during connect to ensure we have the latest environment/settings
        self.command = command
        self.args = args
        self.session: Optional[ClientSession] = None
        self._exit_stack = None
        self._stdio_context = None

    async def connect(self):
        """Connects to the MCP server via stdio."""
        if self.session:
            return

        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        
        # Pass S3 credentials to the MCP server subprocess
        env = os.environ.copy()
        env.update({
            "S3_ENDPOINT_URL": settings.S3_ENDPOINT_URL,
            "S3_ACCESS_KEY": settings.S3_ACCESS_KEY,
            "S3_SECRET_KEY": settings.S3_SECRET_KEY,
        })

        server_parameters = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=env
        )

        try:
            # Setup stdio client
            self._stdio_context = await self._exit_stack.enter_async_context(stdio_client(server_parameters))
            read_stream, write_stream = self._stdio_context
            
            # Start session
            self.session = await self._exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            
            # Initialize connection
            await self.session.initialize()
            logger.info("Connected to MCP Server successfully.")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP Server: {e}")
            if self._exit_stack:
                await self._exit_stack.aclose()
            raise

    async def disconnect(self):
        """Disconnects from the MCP server."""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self.session = None
            logger.info("Disconnected from MCP Server.")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lists available tools from the MCP server, mapped to OpenAI format."""
        if not self.session:
            await self.connect()
            
        result = await self.session.list_tools()
        tools = []
        for tool in result.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return tools

    async def call_tool(self, name: str, arguments: dict) -> Any:
        """Calls an MCP tool with the specified arguments."""
        if not self.session:
            await self.connect()
            
        logger.info(f"Calling tool: {name} with args: {arguments}")
        result = await self.session.call_tool(name, arguments=arguments)
        
        # Parse MCP CallToolResult (which contains a list of TextContent / etc.)
        outputs = []
        for content in result.content:
            if content.type == "text":
                outputs.append(content.text)
            else:
                outputs.append(str(content))
                
        return "\n".join(outputs)

# The command to run the data-refinery server
# We use uv run to execute the server script inside the correct workspace context
data_refinery_mcp = MCPClientManager(
    command="uv",
    args=["run", "--project", "mcp-servers/data-refinery", "python", "mcp-servers/data-refinery/src/data_refinery/application/server.py"]
)
