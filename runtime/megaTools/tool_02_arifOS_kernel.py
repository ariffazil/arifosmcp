"""
arifosmcp/runtime/megaTools/02_arifOS_kernel.py

444_ROUTER: Primary metabolic conductor
Stage: 444_ROUTER | Trinity: DELTA/PSI | Floors: F4, F11

Modes: kernel, status
"""

from __future__ import annotations

from typing import Any
from fastmcp.dependencies import CurrentContext

from arifosmcp.runtime.models import RuntimeEnvelope


async def arifOS_kernel(
    query: str | None = None,
    payload: dict[str, Any] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: str | None = None,
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
    use_memory: bool = True,
    use_heart: bool = True,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.kernel_router import kernel_intelligent_route

    payload = dict(payload or {})
    payload.update(kwargs)
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

    effective_query = payload.get("query") or query or raw_input or ""

    return await kernel_intelligent_route(
        query=effective_query,
        session_id=session_id,
        payload=payload,
        auth_context=auth_context,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        ctx=ctx or CurrentContext(),
        intent=intent,
        use_memory=use_memory,
        use_heart=use_heart,
        debug=debug,
    )
