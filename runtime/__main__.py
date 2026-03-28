"""CLI entrypoint for arifOS AAA MCP."""

from __future__ import annotations

import os
import sys
from importlib import import_module

from .fastmcp_ext.transports import run_server


def _bootstrap_environment() -> None:
    try:
        module = import_module("arifosmcp.transport.env_bootstrap")
        module.bootstrap_environment()
    except Exception:
        return


def main() -> None:
    _bootstrap_environment()

    mode = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("AAA_MCP_TRANSPORT", "stdio")).lower()
    os.environ["AAA_MCP_TRANSPORT"] = mode
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))

    # For HTTP mode, use the pre-configured app from server.py (includes dashboard)
    if mode in ("http", "streamable-http"):
        import uvicorn

        from .server import app

        uvicorn.run(app, host=host, port=port, log_level="info")
        return

    # Stdio clients only need the MCP kernel, not the full HTTP/WebMCP/A2A surface.
    os.environ.setdefault("ARIFOS_MINIMAL_STDIO", "1")

    from .server import create_aaa_mcp_server

    mcp = create_aaa_mcp_server()

    try:
        run_server(mcp, mode=mode, host=host, port=port)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
