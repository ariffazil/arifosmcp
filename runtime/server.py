"""
arifosmcp/runtime/server.py — arifOS AAA Sovereign Hub - HARDENED

UPGRADE: Global Panic Middleware and Sovereign Domain Hardening.
FIX: Register routes BEFORE creating http_app
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager

import fastmcp
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, FileResponse
from starlette.middleware.cors import CORSMiddleware

from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_3, IS_FASTMCP_2
from arifosmcp.runtime.tools import register_tools, ALL_TOOL_IMPLEMENTATIONS
from arifosmcp.runtime.rest_routes import register_rest_routes

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HARDENING: GLOBAL PANIC MIDDLEWARE
# ---------------------------------------------------------------------------

class GlobalPanicMiddleware(BaseHTTPMiddleware):
    """Intercepts kernel panics and emits a Constitutional VOID."""
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print(f"!!! KERNEL PANIC: {str(e)}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return JSONResponse({
                "status": "void",
                "tool": "kernel_panic_handler",
                "error_message": "F13: System halt due to unhandled kernel exception.",
                "action": "HALT"
            }, status_code=500)

# ---------------------------------------------------------------------------
# SERVER INITIALIZATION
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "arifOS Sovereign Intelligence Kernel",
    version="2026.03.24-HARDENED",
    website_url="https://aaa.arif-fazil.com",
)

# Register Surface FIRST (before creating http_app)
register_tools(mcp)
register_rest_routes(mcp, ALL_TOOL_IMPLEMENTATIONS)

# Register ChatGPT Deep Research tools (search + fetch)
try:
    logger.info("[ChatGPT] Attempting to register tools...")
    from arifosmcp.runtime.chatgpt_integration.chatgpt_tools import register_chatgpt_tools
    logger.info("[ChatGPT] Import successful")
    register_chatgpt_tools(mcp)
    logger.info("[ChatGPT] Deep Research tools registered (search + fetch)")
except Exception as e:
    import traceback
    logger.warning(f"[ChatGPT] Could not register tools: {e}")
    logger.warning(f"[ChatGPT] Traceback: {traceback.format_exc()}")

# THEN create the app with all routes included
# FastMCP 2.x/3.x compatibility
if IS_FASTMCP_3:
    app = mcp.http_app(stateless_http=True)
elif IS_FASTMCP_2:
    # 2.x uses streamable_http_app() or direct mounting
    try:
        app = mcp.streamable_http_app()
    except AttributeError:
        # Fallback: get underlying ASGI app
        app = mcp._mcp_server.app
else:
    raise RuntimeError(f"Unsupported FastMCP version: {fastmcp.__version__}")

app.add_middleware(GlobalPanicMiddleware)

# Strict CORS: Only allow Sovereign Domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


def _attach_protocol_apps() -> None:
    """
    Attach side-protocol apps to the live FastMCP site.

    A2A is mounted under `/a2a`, which matches the advertised REST endpoints.
    WebMCP is mounted at `/` late in route order so its existing `/webmcp`,
    `/.well-known/webmcp`, and `/api/live/*` routes become reachable without
    changing their internal path definitions.
    """
    if not hasattr(app, "mount"):
        return

    try:
        from arifosmcp.runtime.a2a import create_a2a_server

        a2a_server = create_a2a_server(mcp)
        app.mount("/a2a", a2a_server.app, name="a2a")
    except Exception:
        logger.exception("Failed to attach A2A app")

    try:
        from arifosmcp.runtime.webmcp.server import create_webmcp_app

        webmcp_app = create_webmcp_app(mcp)
        app.mount("/", webmcp_app, name="webmcp")
    except Exception:
        logger.exception("Failed to attach WebMCP app")


_attach_protocol_apps()

def create_aaa_mcp_server() -> FastMCP:
    return mcp

if __name__ == "__main__":
    from arifosmcp.runtime.fastmcp_ext.transports import run_server
    run_server(mcp, mode="http", host="0.0.0.0", port=8080)
