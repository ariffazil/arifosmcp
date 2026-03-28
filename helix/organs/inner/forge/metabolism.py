"""
arifosmcp/helix/organs/inner/forge/metabolism.py — The Synthesis Engine

Stage 777: AGI·ASI·FORGE.
Synthesizes solutions and generates artifacts under constitutional governance.
Applies F11 execution gate and integrates PNS·ORCHESTRATE routing.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp.dependencies import CurrentContext

from arifosmcp.runtime.exceptions import InfrastructureFault
from arifosmcp.runtime.fault_codes import MechanicalFaultCode
from arifosmcp.runtime.metrics import helix_tracer
from arifosmcp.runtime.models import RuntimeEnvelope
from arifosmcp.runtime.sessions import resolve_runtime_context


def _resolve_organ_session(
    session_id: str,
    ctx: CurrentContext,
    actor_id: str | None = None,
) -> tuple[str, str]:
    """EXPLICIT SESSION RESOLUTION: Returns (transport_session, resolved_session)."""
    ctx_session = getattr(ctx, "session_id", None) if ctx else None
    transport_session = session_id or ctx_session or "global"
    resolved_ctx = resolve_runtime_context(
        incoming_session_id=transport_session,
        auth_context=None,
        actor_id=actor_id,
        declared_name=None,
    )
    return transport_session, resolved_ctx["resolved_session_id"]


async def agi_asi_forge_metabolism(
    spec: str,
    ctx: CurrentContext,
    session_id: str = "global",
    pns_orchestrate: dict[str, Any] | None = None,
    tools: list[str] | None = None,
) -> RuntimeEnvelope:
    """
    Metabolic function for AGI·ASI·FORGE (Stage 777).

    1. Resolve session continuity (EXPLICIT: no implicit fallback).
    2. Inject PNS·ORCHESTRATE routing signal.
    3. Execute forge synthesis via governance kernel.
    4. Emit organ span and constitutional event.
    """
    transport_session, resolved_session = _resolve_organ_session(session_id, ctx)
    active_session = resolved_session  # OPERATIONAL TRUTH

    with helix_tracer.start_organ_span("AGI\u2013ASI\u00b7FORGE", active_session) as span:
        from arifosmcp.runtime.bridge import call_kernel

        orchestrate_payload = pns_orchestrate or {}
        if tools:
            orchestrate_payload = {**orchestrate_payload, "tools": tools}

        payload = {
            "intent": spec,
            "session_id": active_session,
            "pns_orchestrate": orchestrate_payload,
        }

        try:
            kernel_res = await call_kernel(
                "quantum_eureka_forge", active_session, payload
            )
            envelope = RuntimeEnvelope(**kernel_res)
        except Exception as e:
            raise InfrastructureFault(
                message=f"Forge failure in session {active_session}: {e}",
                fault_code=MechanicalFaultCode.INFRA_DEGRADED,
            )

        if span:
            helix_tracer.record_constitutional_event(
                span,
                "forged",
                {
                    "g": envelope.metrics.truth,
                    "ds": envelope.metrics.entropy_delta,
                    "tools_active": bool(tools),
                    "session_id": active_session,
                },
            )

        return envelope
