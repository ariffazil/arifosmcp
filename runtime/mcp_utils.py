"""Shared MCP runtime utilities used across A2A, WebMCP, and other protocol layers."""

from __future__ import annotations

from typing import Any


def normalize_tool_result(result: Any) -> dict[str, Any]:
    """Normalise any MCP tool return value to a plain dict."""
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    if isinstance(result, dict):
        return result
    return {"result": result}


async def call_mcp_tool(
    mcp_server: Any,
    tool_name: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a named tool on the FastMCP kernel and return a normalised dict.

    Probes for the internal ``_call_tool`` method first, then the public
    ``call_tool`` alias, raising ``RuntimeError`` if neither is found.
    """
    if params is None:
        params = {}

    call = getattr(mcp_server, "_call_tool", None) or getattr(mcp_server, "call_tool", None)
    if not callable(call):
        raise RuntimeError("MCP server does not expose a callable tool interface")

    result = await call(tool_name, params)
    return normalize_tool_result(result)
