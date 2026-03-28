"""FastMCP 2.x / 3.x Compatibility Layer — DITEMPA BUKAN DIBERI

Provides unified API surface for arifOS across FastMCP major versions.
Critical for dual-sovereignty deployment (VPS 3.x + Horizon 2.x).
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable

import fastmcp

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Version Detection
# ═══════════════════════════════════════════════════════════════════════════════

FASTMCP_VERSION = tuple(map(int, fastmcp.__version__.split('.')[:2]))
IS_FASTMCP_3 = FASTMCP_VERSION >= (3, 0)
IS_FASTMCP_2 = not IS_FASTMCP_3

logger.info(f"[COMPAT] FastMCP version: {fastmcp.__version__} (3.x: {IS_FASTMCP_3})")

# ═══════════════════════════════════════════════════════════════════════════════
# Exception Compatibility (Critical Fix for Horizon/2.x)
# ═══════════════════════════════════════════════════════════════════════════════

"""
FastMCP 3.x has: AuthorizationError, FastMCPError, ToolError
FastMCP 2.x has: FastMCPError only (AuthorizationError was added in 3.x)

We create AuthorizationError as a subclass of FastMCPError for 2.x compatibility.
"""

from fastmcp.exceptions import FastMCPError

try:
    from fastmcp.exceptions import ToolError
except ImportError:
    # FastMCP 2.x fallback - ToolError may not exist
    class ToolError(FastMCPError):
        """Tool execution error (2.x compatibility shim)."""
        pass

try:
    from fastmcp.exceptions import AuthorizationError
except ImportError:
    # FastMCP 2.x - AuthorizationError doesn't exist, create compatible version
    class AuthorizationError(FastMCPError):
        """Authorization error (2.x compatibility shim).
        
        Mirrors FastMCP 3.x AuthorizationError API for seamless cross-version usage.
        """
        def __init__(self, message: str = "Unauthorized", *, operation: str | None = None, resource: str | None = None):
            super().__init__(message)
            self.operation = operation
            self.resource = resource

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP App Creation Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

def create_http_app(mcp_instance: FastMCP, stateless_http: bool = True) -> Any:
    """Create HTTP app compatible with FastMCP 2.x and 3.x.
    
    FastMCP 3.x: mcp.http_app(stateless_http=True)
    FastMCP 2.x: mcp.http_app() or mcp.streamable_http_app()
    
    Args:
        mcp_instance: The FastMCP instance
        stateless_http: Whether to use stateless HTTP (3.x only)
    
    Returns:
        ASGI application (Starlette/FastAPI compatible)
    """
    if IS_FASTMCP_3:
        # FastMCP 3.x has stateless_http parameter
        return mcp_instance.http_app(stateless_http=stateless_http)
    else:
        # FastMCP 2.x - use streamable_http_app if available, else http_app
        if hasattr(mcp_instance, 'streamable_http_app'):
            return mcp_instance.streamable_http_app()
        return mcp_instance.http_app()

# ═══════════════════════════════════════════════════════════════════════════════
# Custom Route Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

def custom_route(mcp_instance: FastMCP, path: str, methods: list[str], **kwargs) -> Callable:
    """Register custom HTTP route compatible with FastMCP 2.x and 3.x.
    
    Both versions support @mcp.custom_route() with same signature:
    - path: URL path
    - methods: HTTP methods list
    - name: Optional route name
    - include_in_schema: Whether to include in OpenAPI
    
    This wrapper provides a unified API in case of future changes.
    """
    # Both 2.x and 3.x have custom_route with same API
    return mcp_instance.custom_route(path, methods=methods, **kwargs)

# ═══════════════════════════════════════════════════════════════════════════════
# Transport Mode Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

def get_compatible_transport(preferred: str = "streamable-http") -> str:
    """Get transport mode compatible with current FastMCP version.
    
    FastMCP 3.x supports: "streamable-http", "http", "stdio", "sse"
    FastMCP 2.x supports: "http", "stdio", "sse" (no "streamable-http")
    
    Args:
        preferred: Preferred transport mode
    
    Returns:
        Compatible transport mode string
    """
    if IS_FASTMCP_3:
        return preferred
    
    # FastMCP 2.x - map streamable-http to http
    if preferred == "streamable-http":
        return "http"
    return preferred

# ═══════════════════════════════════════════════════════════════════════════════
# Context Dependencies Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from fastmcp.dependencies import CurrentContext
except ImportError:
    # FastMCP 2.x may not have CurrentContext
    CurrentContext = None  # type: ignore

# ═══════════════════════════════════════════════════════════════════════════════
# Starlette Request/Response Helpers (Version Agnostic)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from starlette.requests import Request
    from starlette.responses import Response, JSONResponse, HTMLResponse, PlainTextResponse
    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False
    Request = None  # type: ignore
    Response = None  # type: ignore
    JSONResponse = None  # type: ignore
    HTMLResponse = None  # type: ignore
    PlainTextResponse = None  # type: ignore

# ═══════════════════════════════════════════════════════════════════════════════
# Middleware Compatibility (for ingress_middleware.py)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response
    
    class GlobalPanicMiddleware(BaseHTTPMiddleware):
        """ASGI middleware for constitutional enforcement (2.x/3.x compatible)."""
        
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            """Process request with constitutional safeguards."""
            # Add request ID for tracing
            request_id = request.headers.get("x-request-id", "unknown")
            
            try:
                response = await call_next(request)
                response.headers["x-request-id"] = request_id
                return response
            except Exception as exc:
                logger.error(f"[PANIC] Request failed: {exc}")
                if JSONResponse:
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": "Internal constitutional violation",
                            "request_id": request_id,
                        }
                    )
                raise
                
except ImportError:
    # Fallback if Starlette not available (shouldn't happen in practice)
    GlobalPanicMiddleware = None  # type: ignore

# ═══════════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════════

def ensure_async(handler: Callable) -> Callable:
    """Ensure handler is async (required by FastMCP custom routes)."""
    if asyncio.iscoroutinefunction(handler):
        return handler
    
    @functools.wraps(handler)
    async def async_wrapper(*args, **kwargs):
        return handler(*args, **kwargs)
    
    return async_wrapper

import asyncio

# ═══════════════════════════════════════════════════════════════════════════════
# Export Symbols
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Version
    "FASTMCP_VERSION",
    "IS_FASTMCP_3",
    "IS_FASTMCP_2",
    
    # Exceptions
    "FastMCPError",
    "AuthorizationError",
    "ToolError",
    
    # Functions
    "create_http_app",
    "custom_route",
    "get_compatible_transport",
    "ensure_async",
    
    # Context
    "CurrentContext",
    
    # Middleware
    "GlobalPanicMiddleware",
    
    # Starlette
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "STARLETTE_AVAILABLE",
]
