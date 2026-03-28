from __future__ import annotations

import logging
import time # Added for start time tracking
from typing import Any

from fastmcp import FastMCP

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Stage, Verdict
from .bridge import call_kernel
from .public_registry import is_public_profile, normalize_tool_profile

logger = logging.getLogger(__name__)


# Tools moved to core are no longer defined here.


async def trace_replay(
    session_id: str = "global",
    limit: int = 20,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Read-only replay of sealed trace history for a session."""
    res = await call_kernel("trace_replay", session_id, {"limit": limit})
    return RuntimeEnvelope(
        tool="trace_replay",
        session_id=session_id,
        stage=Stage.VAULT_999.value,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=res,
        auth_context=auth_context,
    )


async def metabolic_loop(
    session_id: str = "global",
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Legacy orchestration tool preserved for compatibility only."""
    res = await call_kernel("metabolic_loop", session_id, {})
    return RuntimeEnvelope(
        tool="metabolic_loop",
        session_id=session_id,
        stage=Stage.ROUTER_444.value,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=res,
        auth_context=auth_context,
    )


def _register_local_phase2_tools(mcp: FastMCP, profile: str = "full") -> None:
    normalized_profile = normalize_tool_profile(profile)

    # search_reality, ingest_evidence, audit_rules, check_vital, session_memory
    # have all been moved to the primary arifOS core tool surface.

    if not is_public_profile(normalized_profile):
        mcp.tool(
            description=(
                "Use this when you need to replay sealed stage traces for a given session_id "
                "from VAULT999 for explainability or audit. This tool is read-only."
            ),
            annotations={"readOnlyHint": True},
        )(trace_replay)
        mcp.tool(
            description=(
                "Use this only for legacy compatibility. For ChatGPT and remote MCP clients, "
                "prefer `arifOS_kernel` from the core runtime tool surface."
            ),
        )(metabolic_loop)


def _register_aclip_tools(mcp: FastMCP) -> None:
    """Register ACLIP Hardened Tools (Nervous System 9)."""
    from arifosmcp.intelligence import console_tools

    mcp.tool(name="system_health")(console_tools.system_health)
    mcp.tool(name="fs_inspect")(console_tools.fs_inspect)
    mcp.tool(name="chroma_query")(console_tools.chroma_query)
    mcp.tool(name="log_tail")(console_tools.log_tail)
    mcp.tool(name="process_list")(console_tools.process_list)
    mcp.tool(name="net_status")(console_tools.net_status)
    mcp.tool(name="arifos_list_resources")(console_tools.arifos_list_resources)
    mcp.tool(name="arifos_read_resource")(console_tools.arifos_read_resource)
    mcp.tool(name="cost_estimator")(console_tools.cost_estimator)


def register_phase2_tools(mcp: FastMCP, profile: str = "full") -> None:
    """Register legacy capability tools without wiring them into the new loop."""
    normalized_profile = normalize_tool_profile(profile)
    _register_local_phase2_tools(mcp, profile=normalized_profile)
    if not is_public_profile(normalized_profile):
        _register_aclip_tools(mcp)


__all__ = [
    "metabolic_loop",
    "register_phase2_tools",
    "trace_replay",
]
