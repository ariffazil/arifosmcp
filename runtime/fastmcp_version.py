"""
FastMCP Version Detection & Compatibility — DITEMPA BUKAN DIBERI

Single source of truth for FastMCP 2.x/3.x cross-version compatibility.
Ensures arifOS runs on both VPS (3.x) and Horizon (2.x) deployments.
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable

import fastmcp
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Version Detection
# ═══════════════════════════════════════════════════════════════════════════════

_version_parts = fastmcp.__version__.split('.')
VERSION_MAJOR = int(_version_parts[0])
VERSION_MINOR = int(_version_parts[1]) if len(_version_parts) > 1 else 0

IS_FASTMCP_3 = VERSION_MAJOR >= 3
IS_FASTMCP_2 = VERSION_MAJOR == 2

logger.info(f"[COMPAT] FastMCP version: {fastmcp.__version__} (3.x: {IS_FASTMCP_3})")

# ═══════════════════════════════════════════════════════════════════════════════
# Exception Compatibility (Critical for Horizon/2.x)
# ═══════════════════════════════════════════════════════════════════════════════

from fastmcp.exceptions import FastMCPError

try:
    from fastmcp.exceptions import ToolError
    HAS_TOOL_ERROR = True
except ImportError:
    HAS_TOOL_ERROR = False
    
    class ToolError(FastMCPError):
        """Tool execution error (FastMCP 2.x compatibility shim)."""
        pass

try:
    from fastmcp.exceptions import AuthorizationError
    HAS_AUTHORIZATION_ERROR = True
except ImportError:
    HAS_AUTHORIZATION_ERROR = False
    
    # FastMCP 2.x - AuthorizationError doesn't exist, create compatible version
    # that matches FastMCP 3.x AuthorizationError API
    class AuthorizationError(FastMCPError):
        """Authorization error (FastMCP 2.x compatibility shim).
        
        Mirrors FastMCP 3.x AuthorizationError API for seamless cross-version usage.
        Note: FastMCP 3.x AuthorizationError only takes message argument.
        """
        def __init__(self, message: str = "Unauthorized"):
            super().__init__(message)

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP App Creation Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

HAS_STATELESS_HTTP = IS_FASTMCP_3  # 3.x: mcp.http_app(stateless_http=True)
HAS_STREAMABLE_HTTP_APP = hasattr(FastMCP, 'streamable_http_app')  # 2.x: mcp.streamable_http_app()
HAS_HTTP_APP = hasattr(FastMCP, 'http_app')

def create_http_app(mcp_instance: FastMCP, stateless_http: bool = True) -> Any:
    """Create HTTP app compatible with FastMCP 2.x and 3.x.
    
    FastMCP 3.x: mcp.http_app(stateless_http=True)
    FastMCP 2.x: mcp.http_app() or mcp.streamable_http_app()
    """
    if IS_FASTMCP_3:
        return mcp_instance.http_app(stateless_http=stateless_http)
    
    # FastMCP 2.x
    if HAS_STREAMABLE_HTTP_APP:
        return mcp_instance.streamable_http_app()
    if HAS_HTTP_APP:
        return mcp_instance.http_app()
    
    raise RuntimeError("No HTTP app method available on FastMCP instance")

# ═══════════════════════════════════════════════════════════════════════════════
# Custom Route Compatibility  
# ═══════════════════════════════════════════════════════════════════════════════

HAS_CUSTOM_ROUTE = hasattr(FastMCP, 'custom_route')
HAS_ROUTE = hasattr(FastMCP, 'route')

def custom_route(mcp_instance: FastMCP, path: str, methods: list[str], **kwargs) -> Callable:
    """Register custom HTTP route compatible with FastMCP 2.x and 3.x.
    
    Both versions support @mcp.custom_route() with the same signature:
    - path: URL path (e.g., "/health")
    - methods: HTTP methods list (e.g., ["GET"])
    - name: Optional route name for reverse URL lookup
    - include_in_schema: Whether to include in OpenAPI schema (default: True)
    
    The handler must be an async function accepting a Starlette Request
    and returning a Starlette Response.
    """
    if HAS_CUSTOM_ROUTE:
        return mcp_instance.custom_route(path, methods=methods, **kwargs)
    elif HAS_ROUTE:
        # Fallback to route() if custom_route not available
        return mcp_instance.route(path, methods=methods, **kwargs)
    else:
        raise RuntimeError("FastMCP instance has no custom_route or route method")

# ═══════════════════════════════════════════════════════════════════════════════
# Transport Mode Compatibility
# ═══════════════════════════════════════════════════════════════════════════════

def get_compatible_transport(preferred: str = "streamable-http") -> str:
    """Get transport mode compatible with current FastMCP version.
    
    FastMCP 3.x: "streamable-http", "http", "stdio", "sse"
    FastMCP 2.x: "http", "stdio", "sse" (no "streamable-http")
    """
    if IS_FASTMCP_3:
        return preferred
    
    # FastMCP 2.x - map streamable-http to http
    if preferred == "streamable-http":
        return "http"
    return preferred

# ═══════════════════════════════════════════════════════════════════════════════
# Starlette Compatibility Check
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from starlette.requests import Request
    from starlette.responses import Response, JSONResponse
    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False
    Request = None  # type: ignore
    Response = None  # type: ignore
    JSONResponse = None  # type: ignore

# ═══════════════════════════════════════════════════════════════════════════════
# Export Symbols
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Version
    'VERSION_MAJOR',
    'VERSION_MINOR',
    'IS_FASTMCP_3',
    'IS_FASTMCP_2',
    
    # Feature flags
    'HAS_STATELESS_HTTP',
    'HAS_STREAMABLE_HTTP_APP',
    'HAS_HTTP_APP',
    'HAS_CUSTOM_ROUTE',
    'HAS_ROUTE',
    'HAS_AUTHORIZATION_ERROR',
    'HAS_TOOL_ERROR',
    
    # Exceptions
    'FastMCPError',
    'AuthorizationError',
    'ToolError',
    
    # Functions
    'create_http_app',
    'custom_route',
    'get_compatible_transport',
    
    # Starlette
    'Request',
    'Response',
    'JSONResponse',
    'STARLETTE_AVAILABLE',
]
