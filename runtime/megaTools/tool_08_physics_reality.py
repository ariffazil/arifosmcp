"""
arifosmcp/runtime/megaTools/08_physics_reality.py

111_SENSE: Earth-Witness fact acquisition and mapping
Stage: 111_SENSE | Trinity: DELTA Δ | Floors: F2, F3, F10

Modes: search, ingest, compass, atlas, time
"""

from __future__ import annotations

from typing import Any
from fastmcp.dependencies import CurrentContext

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_internal import physics_reality_dispatch_impl
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP


async def physics_reality(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: Any | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    debug: bool = False,
    request_id: str | None = None,
    timestamp: str | None = None,
    raw_input: str | None = None,
    ctx: Any | None = None,
) -> RuntimeEnvelope:
    payload = dict(payload or {})
    if raw_input:
        payload.setdefault("query", raw_input)
    if caller_context:
        payload.setdefault("caller_context", caller_context)
    if auth_context:
        payload.setdefault("auth_context", auth_context)
    if query:
        payload.setdefault("query", query)
    if session_id:
        payload.setdefault("session_id", session_id)
    if actor_id:
        payload.setdefault("actor_id", actor_id)
    if intent:
        payload.setdefault("intent", intent)
    if human_approval:
        payload.setdefault("human_approval", human_approval)

    if "physics_reality" in HARDENED_DISPATCH_MAP:
        if mode is None:
            mode = "search"
        res_dict = await HARDENED_DISPATCH_MAP["physics_reality"](mode=mode, payload=payload)
        
        # ─── V1.0 VERDICT FORGING ───
        from arifosmcp.runtime.verdict_wrapper import forge_verdict
        from arifosmcp.runtime.models import CanonicalMetrics
        
        metrics = CanonicalMetrics()
        metrics.telemetry.ds = res_dict.get("metrics", {}).get("telemetry", {}).get("ds", 0.0)
        
        return forge_verdict(
            tool_id="physics_reality",
            stage="111_SENSE",
            payload=res_dict.get("payload", res_dict),
            session_id=session_id,
            metrics=metrics,
            floors_checked=["F2", "F3", "F10"],
            message=res_dict.get("note")
        )

    resolved_payload = dict(payload or {})
    return await physics_reality_dispatch_impl(
        mode=mode,
        payload=resolved_payload,
        auth_context=resolved_payload.get("auth_context", auth_context),
        risk_tier=resolved_payload.get("risk_tier", risk_tier),
        dry_run=bool(resolved_payload.get("dry_run", dry_run)),
        ctx=ctx or CurrentContext(),
    )
