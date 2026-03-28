"""
arifosmcp/runtime/ingress_middleware.py

Ingress tolerance middleware.
"Masuk longgar, dalam tetap governed."
Accept messy input at the boundary; governance enforces inside.

FastMCP 2.x/3.x Compatibility: Middleware API differs between versions.
- 3.x: Uses Middleware base class with on_call_tool hook
- 2.x: Middleware not available — this module provides a no-op fallback
"""
from __future__ import annotations

import logging
import time
from typing import Any

from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_3

logger = logging.getLogger(__name__)

try:
    from arifosmcp.runtime.metrics import REQUESTS_TOTAL, METABOLIC_LOOP_DURATION, SABAR_EVENTS
    _METRICS_AVAILABLE = True
except Exception:
    _METRICS_AVAILABLE = False

# The 11 mega-tools — enforce ingress tolerance on all of them
MEGA_TOOLS = {
    "init_anchor", "arifOS_kernel", "apex_soul", "vault_ledger",
    "agi_mind", "asi_heart", "engineering_memory", "physics_reality",
    "math_estimator", "code_engine", "architect_registry",
}

# Mode synonym normalization: obvious variants → canonical mode names
# Principle: never reject what we can obviously understand
MODE_SYNONYMS: dict[str, dict[str, str]] = {
    "agi_mind": {
        "think": "reason", "analyze": "reason", "analyse": "reason",
        "ask": "reason", "query": "reason", "recommend": "reason",
        "ponder": "reason", "evaluate": "reason", "assess": "reason",
        "reflect_on": "reflect", "mirror": "reflect",
        "build": "forge", "create": "forge", "generate": "forge",
    },
    "asi_heart": {
        "check": "critique", "review": "critique", "audit": "critique",
        "test": "critique", "validate": "critique",
        "model": "simulate", "project": "simulate", "predict": "simulate",
    },
    "physics_reality": {
        "find": "search", "lookup": "search", "look_up": "search",
        "fetch": "ingest", "load": "ingest", "import": "ingest",
        "navigate": "compass", "explore": "compass", "map": "atlas",
        "now": "time", "datetime": "time", "date": "time", "clock": "time",
    },
    "arifOS_kernel": {
        "run": "kernel", "execute": "kernel", "process": "kernel",
        "think": "kernel", "reason": "kernel",
        "health": "status", "ping": "status", "check": "status",
    },
    "init_anchor": {
        "start": "init", "begin": "init", "login": "init", "connect": "init",
        "check": "state", "info": "state", "whoami": "state",
        "logout": "revoke", "disconnect": "revoke", "end": "revoke",
        "renew": "refresh", "extend": "refresh", "update": "refresh",
    },
    "apex_soul": {
        "check": "validate", "review": "validate", "audit": "judge",
        "block": "hold", "pause": "hold", "freeze": "hold",
        "test": "probe", "ping": "probe",
    },
    "vault_ledger": {
        "save": "seal", "store": "seal", "commit": "seal", "record": "seal",
        "check": "verify", "validate": "verify", "confirm": "verify",
    },
    "engineering_memory": {
        "build": "engineer", "do": "engineer", "run": "engineer",
        "search": "vector_query", "find": "vector_query", "recall": "vector_query",
        "remember": "vector_store", "save": "vector_store", "store": "vector_store",
        "forget": "vector_forget", "delete": "vector_forget", "remove": "vector_forget",
        "write": "generate", "draft": "generate", "make": "generate",
    },
    "code_engine": {
        "files": "fs", "list": "fs", "dir": "fs",
        "ps": "process", "tasks": "process", "jobs": "process",
        "network": "net", "connections": "net",
        "logs": "tail", "log": "tail",
    },
    "math_estimator": {
        "price": "cost", "estimate": "cost", "budget": "cost",
        "status": "health", "check": "health",
        "metrics": "vitals", "stats": "vitals",
    },
    "architect_registry": {
        "add": "register", "create": "register",
        "show": "list", "ls": "list", "all": "list",
        "get": "read", "fetch": "read", "load": "read",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# FastMCP 3.x Middleware (Full functionality)
# ═══════════════════════════════════════════════════════════════════════════════

if IS_FASTMCP_3:
    try:
        from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext, CallNext, ToolResult
        import mcp.types as mt
        
        class IngressToleranceMiddleware(Middleware):
            """
            Strip unknown fields from tool arguments before they reach Pydantic.

            Doctrine:
              - entry: adaptive (accept any field)
              - core: governed (strict after normalization)
              - output: strong
            """

            def __init__(self, tool_param_sets: dict[str, set[str]] | None = None) -> None:
                self._tool_param_sets: dict[str, set[str]] = tool_param_sets or {}

            def register_tool_params(self, tool_name: str, param_names: set[str]) -> None:
                self._tool_param_sets[tool_name] = param_names

            async def on_call_tool(
                self,
                context: MiddlewareContext[mt.CallToolRequestParams],
                call_next: CallNext[mt.CallToolRequestParams, ToolResult],
            ) -> ToolResult:
                msg = context.message
                tool_name = msg.name

                if tool_name in MEGA_TOOLS and msg.arguments:
                    # 1. Mode synonym normalization: "recommend" → "reason", etc.
                    if "mode" in msg.arguments:
                        synonyms = MODE_SYNONYMS.get(tool_name, {})
                        raw_mode = str(msg.arguments["mode"]).lower().strip()
                        canonical = synonyms.get(raw_mode)
                        if canonical:
                            logger.debug(
                                "Ingress: normalizing mode '%s' → '%s' for tool '%s'",
                                raw_mode, canonical, tool_name,
                            )
                            msg.arguments["mode"] = canonical

                    # 2. Unknown field absorption: strip fields Pydantic doesn't know about
                    known = self._tool_param_sets.get(tool_name)
                    if known is not None:
                        unknown = {k for k in msg.arguments if k not in known}
                        if unknown:
                            logger.debug(
                                "Ingress tolerance: absorbing unknown fields %s for tool '%s'",
                                unknown, tool_name,
                            )
                            # Mutate in place — context is transient per request
                            for k in unknown:
                                msg.arguments.pop(k)

                # Instrument: track latency and call count per tool
                t0 = time.monotonic()
                result = await call_next(context)
                if _METRICS_AVAILABLE and tool_name in MEGA_TOOLS:
                    elapsed = time.monotonic() - t0
                    try:
                        REQUESTS_TOTAL.labels(method=tool_name, status="ok").inc()
                        METABOLIC_LOOP_DURATION.observe(elapsed)
                    except Exception:
                        pass
                return result
                
    except ImportError as e:
        logger.warning(f"[COMPAT] Could not import FastMCP 3.x middleware: {e}")
        # Fall through to no-op fallback
        IS_FASTMCP_3 = False

# ═══════════════════════════════════════════════════════════════════════════════
# FastMCP 2.x Fallback (No-op — middleware not available)
# ═══════════════════════════════════════════════════════════════════════════════

if not IS_FASTMCP_3:
    class IngressToleranceMiddleware:
        """
        No-op fallback for FastMCP 2.x (middleware API not available).
        
        FastMCP 2.x doesn't have the Middleware base class, so we provide
        a compatible no-op that won't break the server but also won't provide
        ingress tolerance features.
        """
        
        def __init__(self, tool_param_sets: dict[str, set[str]] | None = None) -> None:
            self._tool_param_sets: dict[str, set[str]] = tool_param_sets or {}

        def register_tool_params(self, tool_name: str, param_names: set[str]) -> None:
            """Store param names (no-op in 2.x)."""
            self._tool_param_sets[tool_name] = param_names

        async def on_call_tool(self, *args, **kwargs) -> Any:
            """Pass through — no middleware in 2.x."""
            # In 2.x, we can't hook into the call chain, so this is never called
            # It's here for API compatibility
            pass


# Export
__all__ = ["IngressToleranceMiddleware", "MODE_SYNONYMS", "MEGA_TOOLS"]
