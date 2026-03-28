"""
arifosmcp.intelligence.cli — The ACLIP Console for AI MCP Server.

This server provides local operation tools for AI agents, allowing them to
inspect system health, processes, filesystem, logs, and network status
without the full constitutional overhead of the governance kernel.

Identity: aclip-cai
Motto: DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

from arifosmcp.intelligence import console_tools
from arifosmcp.runtime.fastmcp_ext.transports import run_server


def create_aclip_server() -> FastMCP:
    """Create and configure the aclip-cai MCP server."""
    mcp = FastMCP(
        "aclip-cai",
        instructions="ACLIP — Console for AI on arifOS (Nervous System 9 Tools)",
    )

    # Register Nervous System 9 Tools
    mcp.tool(name="system_health")(console_tools.system_health)
    mcp.tool(name="process_list")(console_tools.process_list)
    mcp.tool(name="fs_inspect")(console_tools.fs_inspect)
    mcp.tool(name="log_tail")(console_tools.log_tail)
    mcp.tool(name="net_status")(console_tools.net_status)
    mcp.tool(name="chroma_query")(console_tools.chroma_query)
    mcp.tool(name="arifos_list_resources")(console_tools.arifos_list_resources)
    mcp.tool(name="arifos_read_resource")(console_tools.arifos_read_resource)
    mcp.tool(name="cost_estimator")(console_tools.cost_estimator)

    return mcp


def main() -> None:
    """Main entry point for the aclip-cai server."""
    mcp = create_aclip_server()

    mode = os.getenv("ACLIP_TRANSPORT", "stdio").lower()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8081"))  # Default to 8081 to avoid conflict with arifos (8080)

    # For HTTP mode, use fastmcp's direct runner if needed or the standardized run_server
    if mode in ("http", "streamable-http"):
        import uvicorn

        # Note: Static files or extra middleware can be added here if needed
        app = mcp.http_app(stateless_http=True)
        uvicorn.run(app, host=host, port=port, log_level="info")
        return

    run_server(mcp, mode=mode, host=host, port=port)


if __name__ == "__main__":
    main()
