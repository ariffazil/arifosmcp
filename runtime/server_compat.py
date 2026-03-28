"""
arifOS Server - FastMCP Version Compatibility Layer

This module provides a unified interface that works with BOTH:
- FastMCP 2.x (Prefect Horizon)
- FastMCP 3.x (VPS, local development)

Usage:
    from arifosmcp.runtime.server_compat import create_mcp_server
    
    mcp = create_mcp_server("arifOS")
    
    @mcp.tool()
    def my_tool():
        pass
"""

import sys
from typing import Any, Callable, Optional

# Detect FastMCP version
try:
    import fastmcp
    FASTMCP_VERSION = tuple(map(int, fastmcp.__version__.split('.')[:2]))
except (ImportError, AttributeError):
    FASTMCP_VERSION = (2, 0)  # Assume 2.x if can't detect

IS_FASTMCP_3 = FASTMCP_VERSION[0] >= 3


def create_mcp_server(
    name: str,
    version: str = "2026.03.28",
    **kwargs
) -> Any:
    """
    Create an MCP server that works with FastMCP 2.x or 3.x
    """
    if IS_FASTMCP_3:
        # FastMCP 3.x - modern API
        from fastmcp import FastMCP
        return FastMCP(name, version=version, **kwargs)
    else:
        # FastMCP 2.x - legacy API
        from fastmcp import FastMCP
        # 2.x doesn't support version parameter
        return FastMCP(name)


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> Callable:
    """
    Decorator that works with both FastMCP 2.x and 3.x
    """
    def decorator(func: Callable) -> Callable:
        if IS_FASTMCP_3:
            # FastMCP 3.x - can use decorator with args
            from fastmcp import FastMCP
            # Return the decorator directly
            return FastMCP.tool(name=name, description=description, **kwargs)(func)
        else:
            # FastMCP 2.x - simpler decorator
            from fastmcp import FastMCP
            mcp = FastMCP._current_instance
            if mcp:
                return mcp.tool()(func)
            return func
    return decorator


def run_server(mcp: Any, transport: str = "stdio", **kwargs) -> None:
    """
    Run server with version-appropriate API
    """
    if IS_FASTMCP_3:
        # FastMCP 3.x
        mcp.run(transport=transport, **kwargs)
    else:
        # FastMCP 2.x
        if transport == "stdio":
            mcp.run()
        elif transport == "http":
            host = kwargs.get('host', '0.0.0.0')
            port = kwargs.get('port', 8000)
            mcp.run(transport='http', host=host, port=port)
        else:
            mcp.run()


# Export version info
__all__ = [
    'create_mcp_server',
    'tool',
    'run_server',
    'IS_FASTMCP_3',
    'FASTMCP_VERSION',
]
