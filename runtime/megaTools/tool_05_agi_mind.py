"""
arifosmcp/runtime/megaTools/05_agi_mind.py

333_MIND: Core reasoning and synthesis engine
Stage: 333_MIND | Trinity: DELTA Δ | Floors: F2, F4, F7, F8

Modes: reason, reflect, forge
"""

from __future__ import annotations

from typing import Any

# FastMCP 2.x/3.x compatibility
try:
    from fastmcp.dependencies import CurrentContext
except ImportError:
    # FastMCP 2.x doesn't have dependencies module
    CurrentContext = None

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_internal import agi_mind_dispatch_impl
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP


async def agi_mind(
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
    constitutional_context: str | None = None,
    telos_manifold: dict | None = None,
    previous_coherence: float | None = None,
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
    if constitutional_context:
        payload.setdefault("constitutional_context", constitutional_context)
    if telos_manifold:
        payload.setdefault("telos_manifold", telos_manifold)
    if previous_coherence is not None:
        payload.setdefault("previous_coherence", previous_coherence)
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

    if "agi_mind" in HARDENED_DISPATCH_MAP:
        if mode is None:
            mode = "reason"
        res_dict = await HARDENED_DISPATCH_MAP["agi_mind"](mode=mode, payload=payload)

        # ─── V1.0 VERDICT FORGING ───
        from arifosmcp.runtime.verdict_wrapper import forge_verdict
        from arifosmcp.runtime.models import CanonicalMetrics

        # Extract metrics from hardened result
        metrics = CanonicalMetrics()
        metrics.telemetry.ds = res_dict.get("metrics", {}).get("telemetry", {}).get("ds", 0.0)
        metrics.telemetry.confidence = res_dict.get("confidence", 0.5)

        return forge_verdict(
            tool_id="agi_mind",
            stage="333_MIND",
            payload=res_dict.get("payload", res_dict),
            session_id=session_id,
            metrics=metrics,
            floors_checked=["F2", "F4", "F7", "F8"],
            message=res_dict.get("note")
        )

    resolved_payload = dict(payload or {})
    res = await agi_mind_dispatch_impl(
        mode=mode,
        payload=resolved_payload,
        auth_context=resolved_payload.get("auth_context", auth_context),
        risk_tier=resolved_payload.get("risk_tier", risk_tier),
        dry_run=bool(resolved_payload.get("dry_run", dry_run)),
        ctx=ctx or (CurrentContext() if CurrentContext else None),
    )
    
    # ─── V1.0 VERDICT FORGING (FALLBACK) ───
    if not hasattr(res, "verdict_detail") or not res.verdict_detail:
        from arifosmcp.runtime.verdict_wrapper import forge_verdict
        return forge_verdict(
            tool_id="agi_mind",
            stage=res.stage,
            payload=res.payload,
            session_id=session_id,
            override_code=VerdictCode(res.verdict.value) if hasattr(res.verdict, "value") else VerdictCode.SABAR,
            message=res.payload.get("note", "Fallback reasoning active.")
        )
    return res
