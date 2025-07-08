import asyncio
import os
from typing import Optional
import httpx

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
                self.client = httpx.AsyncClient(
                    base_url=self.server_url,
                    timeout=30.0
                )

    async def call_tool(self, name: str, arguments: dict) -> str:
        """
        Call a tool on the MCP server using JSON-RPC 2.0.
        """
        rpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }

        async with httpx.AsyncClient(base_url=self.server_url) as client:
            response = await client.post("/mcp", json=rpc_request)
            response.raise_for_status()
            rpc_response = response.json()

            if rpc_response is None:
                return "Error: Received None response from MCP server"

            if "error" in rpc_response and rpc_response["error"] is not None:
                error_info = rpc_response["error"]
                if isinstance(error_info, dict):
                    error_message = error_info.get('message', 'Unknown error')
                    error_code = error_info.get('code', 'Unknown code')
                    return f"MCP Error [{error_code}]: {error_message}"
                else:
                    return f"MCP Error: {error_info}"

            result = rpc_response.get("result")
            if result is None:
                return "Error: No result field in MCP response"

            content = result.get("content", [])

            if content and len(content) > 0:
                first_content = content[0]
                if first_content and isinstance(first_content, dict):
                    text_content = first_content.get("text", "No text content available")
                    return text_content
                else:
                    return f"Unexpected content format: {first_content}"

            return f"No content returned. Full result: {result}"


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