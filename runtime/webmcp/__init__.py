"""
arifOS WebMCP Extension
The first AI-governed WebMCP environment on the internet.

WebMCP extends MCP to browsers with constitutional enforcement (F1-F13).
Every HTTP request passes through the 000→999 metabolic loop.

Usage:
    from arifosmcp.runtime.webmcp import WebMCPGateway
    
    gateway = WebMCPGateway(mcp_server)
    app = gateway.app  # FastAPI app with web routes

Motto: Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]
"""

from __future__ import annotations

__version__ = "2026.03.14-VALIDATED"
__all__ = ["WebMCPGateway", "WebMCPConfig", "WebSession"]

from .server import WebMCPGateway, WebMCPConfig
from .session import WebSession
