"""FastMCP extension layer for arifOS AAA MCP.

This package isolates FastMCP-specific integration concerns outside `core/`.
"""

from .discovery import build_surface_discovery
from .transports import run_server

__all__ = [
    "run_server",
    "build_surface_discovery",
]
