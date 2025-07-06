import asyncio
import os
from typing import Dict, Any, Optional


class MCPToolExecutor:
    """
    Handles communication with MCP server for tool execution.
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.client = None
        self._client_lock = asyncio.Lock()
    
    async def ensure_connection(self) -> None:
        """Ensure we have a valid connection to the MCP server."""
        async with self._client_lock:
            if self.client is None or self.client.is_closed:
                import httpx
                self.client = httpx.AsyncClient(base_url=self.server_url)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.
        
        Args:
            name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
            
        Returns:
            Result from the tool execution
        """
        await self.ensure_connection()
        
        try:
            response = await self.client.post("/tools/call", json={
                "name": name,
                "arguments": arguments
            })
            response.raise_for_status()
            result = response.json()
            return result.get("result", "No result")
        except Exception as e:
            return f"Error calling MCP tool: {str(e)}"
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        async with self._client_lock:
            if self.client and not self.client.is_closed:
                await self.client.aclose()
                self.client = None


# Global instance
_mcp_executor: Optional[MCPToolExecutor] = None


def get_mcp_executor() -> MCPToolExecutor:
    """Get or create the global MCP executor instance."""
    global _mcp_executor
    if _mcp_executor is None:
        server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        _mcp_executor = MCPToolExecutor(server_url=server_url)
    return _mcp_executor


async def cleanup_mcp_executor() -> None:
    """Clean up the global MCP executor instance."""
    global _mcp_executor
    if _mcp_executor is not None:
        await _mcp_executor.disconnect()
        _mcp_executor = None