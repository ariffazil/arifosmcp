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
        res = await HARDENED_DISPATCH_MAP["agi_mind"](mode=mode, payload=payload)
        if isinstance(res, dict):
            ok = res.get("ok", res.get("status") not in ("HOLD", "ERROR", "VOID", None))
            _next_tools = res.get("next_allowed_tools", [])
            _payload = res.get("payload", res) if isinstance(res.get("payload"), dict) else res
            _hold_reason = res.get("warnings", [""])[0] if res.get("warnings") else ""
            _next_action = None
            if not ok and _hold_reason:
                _next_action = {
                    "reason": _hold_reason,
                    "missing_requirements": _payload.get("missing_requirements", [])
                    if isinstance(_payload, dict)
                    else [],
                    "next_allowed_tools": _next_tools,
                    "suggested_canonical_call": _payload.get("suggested_canonical_call")
                    if isinstance(_payload, dict)
                    else None,
                }
            return RuntimeEnvelope(
                tool=res.get("tool", "unknown"),
                stage=res.get("stage", "444_ROUTER"),
                status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
                verdict=Verdict.SEAL if ok else Verdict.VOID,
                allowed_next_tools=_next_tools,
                next_action=_next_action,
                payload=res,
            )
        return res

    resolved_payload = dict(payload or {})
    return await agi_mind_dispatch_impl(
        mode=mode,
        payload=resolved_payload,
        auth_context=resolved_payload.get("auth_context", auth_context),
        risk_tier=resolved_payload.get("risk_tier", risk_tier),
        dry_run=bool(resolved_payload.get("dry_run", dry_run)),
        ctx=ctx or (CurrentContext() if CurrentContext else None),
    )
