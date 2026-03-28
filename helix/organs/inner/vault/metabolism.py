"""
arifosmcp/helix/organs/inner/vault/metabolism.py — The Immutable Ledger

Stage 999: VAULT·SEAL.
Commits the sovereign verdict to VAULT999.
Updates the Cooling Ledger with a hash-chain entry.
Enforces F1 Amanah: only SEAL, HOLD_888, PARTIAL, and SABAR may be committed.
VOID verdicts indicate constitutional collapse and cannot be sealed.

Includes post-seal hybrid memory sync (LanceDB hot cache refresh).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging

from fastmcp.dependencies import CurrentContext

logger = logging.getLogger(__name__)

from arifosmcp.runtime.exceptions import ConstitutionalViolation, InfrastructureFault
from arifosmcp.runtime.fault_codes import ConstitutionalFaultCode, MechanicalFaultCode
from arifosmcp.runtime.metrics import helix_tracer
from arifosmcp.runtime.models import RuntimeEnvelope
from arifosmcp.runtime.sessions import resolve_runtime_context


_SEALABLE_VERDICTS = {"SEAL", "HOLD_888", "PARTIAL", "SABAR"}


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


async def vault_seal_metabolism(
    verdict: str,
    evidence: str,
    ctx: CurrentContext,
    session_id: str = "global",
) -> RuntimeEnvelope:
    """
    Metabolic function for VAULT·SEAL (Stage 999).

    1. Resolve session continuity (EXPLICIT: no implicit fallback).
    2. Enforce F1 Amanah: only valid verdicts may seal.
    3. Commit verdict + evidence to VAULT999 via governance kernel.
    4. Emit organ span and constitutional event.
    """
    transport_session, resolved_session = _resolve_organ_session(session_id, ctx)
    active_session = resolved_session  # OPERATIONAL TRUTH

    with helix_tracer.start_organ_span("VAULT\u00b7SEAL", active_session) as span:
        # F1 Amanah: VOID cannot be sealed — it is evidence of collapse
        if verdict not in _SEALABLE_VERDICTS:
            raise ConstitutionalViolation(
                message=(
                    f"F1 Amanah: '{verdict}' cannot be committed to VAULT999. "
                    f"Only {_SEALABLE_VERDICTS} may seal. VOID indicates collapse."
                ),
                floor_code=ConstitutionalFaultCode.F13_SOVEREIGN_VETO,
                extra={"attempted_verdict": verdict},
            )

        from arifosmcp.runtime.bridge import call_kernel

        payload = {
            "summary": f"Sealed commit for session {active_session}",
            "verdict": verdict,
            "evidence": evidence,
            "session_id": active_session,
        }

        try:
            kernel_res = await call_kernel(
                "seal_vault_commit", active_session, payload
            )
            envelope = RuntimeEnvelope(**kernel_res)
        except Exception as e:
            raise InfrastructureFault(
                message=f"Vault seal failure in session {active_session}: {e}",
                fault_code=MechanicalFaultCode.INFRA_DEGRADED,
            )

        if span:
            helix_tracer.record_constitutional_event(
                span,
                "sealed",
                {"verdict": verdict, "session_id": active_session},
            )
        
        # Post-seal: Trigger hybrid memory sync (daily vectors → LanceDB)
        # This ensures L3 hot cache is fresh for next session
        asyncio.create_task(_sync_hybrid_memory_post_seal(active_session))

        return envelope


async def _sync_hybrid_memory_post_seal(session_id: str):
    """
    Post-VAULT999 sync: Update LanceDB hot cache from Qdrant.
    
    Called after each seal to ensure vector continuity.
    F1: Non-blocking; failures logged but don't block seal.
    """
    try:
        import asyncio
        from arifosmcp.intelligence.tools.hybrid_vector_memory import get_hybrid_memory
        
        memory = await get_hybrid_memory()
        await memory.sync_from_qdrant(days=1)  # Sync last 24h
        
        logger.info(f"Post-seal hybrid memory sync complete for {session_id}")
        
    except Exception as e:
        # F1: Log but don't fail — Qdrant remains source of truth
        logger.warning(f"Post-seal hybrid sync failed (non-critical): {e}")
