"""
WebMCP Configuration
Constitutional defaults for web-facing MCP.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class WebMCPConfig:
    """
    WebMCP configuration with constitutional defaults.
    
    All settings enforce F11 (Command Auth) and F12 (Injection Guard).
    """
    
    # CORS - F12 Injection Guard validates origins
    # Note: TrustedHostMiddleware expects just the host pattern (no scheme)
    ALLOWED_ORIGINS: Set[str] = frozenset([
        "arifosmcp.arif-fazil.com",
        "*.arif-fazil.com",
        "arifos.arif-fazil.com",
        "localhost",
        "localhost:3000",      # Dev only
        "localhost:5173",      # Vite dev
        "localhost:8080",      # Local testing
    ])
    
    # Session - F11 Command Auth
    SESSION_TTL: int = 3600          # 1 hour
    SESSION_COOKIE: str = "arifos_session"
    SESSION_SECURE: bool = True      # HTTPS only
    SESSION_SAMESITE: str = "strict"
    SESSION_HTTPONLY: bool = True    # No JS access
    
    # WebSocket - Real-time governance
    WS_HEARTBEAT: int = 30           # seconds
    WS_MAX_CONNECTIONS: int = 100
    WS_PING_INTERVAL: float = 20.0
    
    # Rate Limiting - F5 Peace² (stability)
    RATE_LIMIT_REQUESTS: int = 100   # per minute
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_BURST: int = 10       # Allow burst
    
    # Constitutional timeouts
    REQUEST_TIMEOUT: float = 30.0    # Max processing time
    METABOLIC_TIMEOUT: float = 60.0  # Full 000→999 loop
    
    # Content Security - F12
    CSP_POLICY: str = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' wss: https:; "
        "img-src 'self' data: https:;"
    )
    
    @classmethod
    def from_env(cls) -> "WebMCPConfig":
        """Load config from environment variables."""
        return cls(
            SESSION_TTL=int(os.getenv("ARIFOS_SESSION_TTL", "3600")),
            SESSION_SECURE=os.getenv("ARIFOS_SESSION_SECURE", "true").lower() == "true",
            RATE_LIMIT_REQUESTS=int(os.getenv("ARIFOS_RATE_LIMIT", "100")),
            WS_MAX_CONNECTIONS=int(os.getenv("ARIFOS_WS_MAX_CONN", "100")),
        )
