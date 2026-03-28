"""
arifosmcp/helix/organs/inner/critique/metabolism.py — The Self-Auditor

Stage 666B: ASI·CRITIQUE.
Evaluates draft output for blind spots, uncertainty, and floor compliance.
Applies F7 Humility gate and integrates PNS·HEALTH + PNS·FLOOR signals.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp.dependencies import CurrentContext

from arifosmcp.runtime.exceptions import ConstitutionalViolation, InfrastructureFault
from arifosmcp.runtime.fault_codes import ConstitutionalFaultCode, MechanicalFaultCode
from arifosmcp.runtime.metrics import helix_tracer
from arifosmcp.runtime.models import RuntimeEnvelope
from arifosmcp.runtime.sessions import resolve_runtime_context


def _resolve_organ_session(
    session_id: str,
    ctx: CurrentContext,
    actor_id: str | None = None,
) -> tuple[str, str]:
    """
    EXPLICIT SESSION RESOLUTION: No implicit fallback to "global" as truth.
    Returns (transport_session, resolved_session) tuple.
    """
    # Get from context if available
    ctx_session = getattr(ctx, "session_id", None) if ctx else None
    
    # Transport is the raw incoming value (for debug/tracing)
    transport_session = session_id or ctx_session or "global"
    
    # Resolve canonical session using the centralized resolver
    # This ensures truth surface consistency across all organs
    resolved_ctx = resolve_runtime_context(
        incoming_session_id=transport_session,
        auth_context=None,  # Organs rely on outer auth context
        actor_id=actor_id,
        declared_name=None,
    )
    
    # Return both: transport for debug/tracing, resolved for operational truth
    return transport_session, resolved_ctx["resolved_session_id"]


async def asi_critique_metabolism(
    draft_output: str,
    ctx: CurrentContext,
    session_id: str = "global",
    pns_health: dict[str, Any] | None = None,
    pns_floor: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """
    Metabolic function for ASI·CRITIQUE (Stage 666B).

    1. Resolve session continuity (EXPLICIT: no implicit fallback).
    2. Inject PNS·HEALTH and PNS·FLOOR signals into the audit payload.
    3. Execute thought audit against the governance kernel.
    4. Enforce F7 Humility gate (confidence must stay in [0.03, 0.05]).
    5. Emit organ span and constitutional event.
    """
    transport_session, resolved_session = _resolve_organ_session(session_id, ctx)
    active_session = resolved_session  # OPERATIONAL TRUTH

    with helix_tracer.start_organ_span("ASI·CRITIQUE", active_session) as span:
        from arifosmcp.runtime.bridge import call_kernel

        payload = {
            "thought_id": "current_thought",
            "draft_output": draft_output,
            "session_id": active_session,
            "pns_health": pns_health,
            "pns_floor": pns_floor,
        }

        try:
            kernel_res = await call_kernel(
                "critique_thought_audit", active_session, payload
            )
            envelope = RuntimeEnvelope(**kernel_res)
        except Exception as e:
            raise InfrastructureFault(
                message=f"Critique failure in session {active_session}: {e}",
                fault_code=MechanicalFaultCode.INFRA_DEGRADED,
            )

        # F7 Humility gate: confidence must stay in [0.03, 0.05]
        omega = envelope.metrics.telemetry.confidence
        if omega < 0.03 or omega > 0.05:
            raise ConstitutionalViolation(
                message=(
                    f"F7 Humility gate breached: confidence {omega:.4f} outside "
                    f"[0.03, 0.05]. Draft may be overconfident or paralysed."
                ),
                floor_code=ConstitutionalFaultCode.F2_TRUTH_BELOW_THRESHOLD,
                extra={"omega": omega},
            )

        if span:
            helix_tracer.record_constitutional_event(
                span,
                "critiqued",
                {
                    "omega": omega,
                    "pns_health_active": pns_health is not None,
                    "pns_floor_active": pns_floor is not None,
                    "session_id": active_session,
                },
            )

        return envelope
