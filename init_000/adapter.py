"""
arifosmcp/init_000/adapter.py

Compatibility adapter: wires init_000 into the existing init_anchor surface.

The existing init_anchor accepts: mode, payload, actor_id, declared_name,
intent, session_id, human_approval, risk_tier, dry_run, etc.

The new init_000 core accepts: deployment_id, requested_role,
provider_key, family_key, session_id.

This adapter:
1. Accepts the OLD init_anchor parameter signature
2. Maps actor_id/deployment_id appropriately
3. Routes to init_anchor_v1_impl for mode="init"
4. Returns InitV1Envelope wrapped in RuntimeEnvelope for backward compat

This lets us replace the core without breaking existing callers.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.init_000.tools import (
    init_anchor_v1_impl,
    get_deployment_impl,
    get_provider_soul_impl,
    get_session_anchor_impl,
    log_drift_event_impl,
)
from arifosmcp.init_000.schemas import SELF_CLAIM_BOUNDARY_V1
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict


def _map_actor_id_to_deployment(actor_id: str | None, payload: dict[str, Any] | None) -> str | None:
    """Map actor_id to deployment_id. In v1, deployment_id IS the identity."""
    if actor_id and actor_id not in ("anonymous", "system"):
        return actor_id
    if payload and payload.get("deployment_id"):
        return payload["deployment_id"]
    return None


def init_anchor_v1_compat(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: Any | None = None,
    human_approval: bool = False,
    human_approved: bool | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict[str, Any] | None = None,
    auth_context: dict | None = None,
    debug: bool = False,
    request_id: str | None = None,
    timestamp: str | None = None,
    raw_input: str | None = None,
    pns_shield: Any | None = None,
    proof: str | None = None,
    ctx: Any | None = None,
    reason: str | None = None,
    use_memory: bool = True,
    use_heart: bool = True,
    use_critique: bool = True,
    context: Any | None = None,
    model_soul: dict[str, Any] | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    """
    Compatibility wrapper: maps old init_anchor signature → new init_000 logic.

    Routing:
    - mode="init" or None → init_anchor_v1_impl (v1 core)
    - mode="state" → get_deployment_impl
    - mode="status" → get_session_anchor_impl (if session_id)
    - mode="revoke" → end_session_anchor (future)
    - mode="refresh" → re-init with same deployment_id (future)
    """
    payload = dict(payload or {})
    effective_mode = mode or "init"

    # ─── MODE: init ───────────────────────────────────────────────────────────
    if effective_mode == "init":
        # Map actor_id → deployment_id (v1 identity IS deployment)
        deployment_id = _map_actor_id_to_deployment(actor_id, payload)

        # Also check payload for deployment_id
        if not deployment_id:
            deployment_id = payload.get("deployment_id")

        # Fall back to actor_id if it looks like a deployment_id
        if not deployment_id:
            deployment_id = actor_id

        requested_role = _map_role(intent, declared_name, payload)

        v1_result = init_anchor_v1_impl(
            deployment_id=deployment_id,
            requested_role=requested_role,
            provider_key=payload.get("provider_key"),
            family_key=payload.get("family_key"),
            session_id=session_id or payload.get("session_id"),
        )

        return _v1_to_runtime_envelope(v1_result, effective_mode, dry_run)

    # ─── MODE: state ──────────────────────────────────────────────────────────
    if effective_mode == "state":
        deployment_id = session_id or actor_id or (payload.get("session_id") if payload else None)
        if not deployment_id:
            return _error_envelope(
                "state mode requires session_id or actor_id",
                mode=effective_mode,
            )
        v1_result = get_deployment_impl(deployment_id)
        return _v1_to_runtime_envelope(v1_result, effective_mode, dry_run)

    # ─── MODE: status ─────────────────────────────────────────────────────────
    if effective_mode == "status":
        lookup_id = session_id or actor_id or (payload.get("session_id") if payload else None)
        if not lookup_id:
            return _error_envelope(
                "status mode requires session_id or actor_id",
                mode=effective_mode,
            )
        v1_result = get_session_anchor_impl(lookup_id)
        return _v1_to_runtime_envelope(v1_result, effective_mode, dry_run)

    # ─── MODE: revoke ─────────────────────────────────────────────────────────
    if effective_mode == "revoke":
        # Future: end_session_anchor
        return RuntimeEnvelope(
            tool="init_anchor",
            stage="000_INIT",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            payload={
                "ok": False,
                "error": "revoke mode not yet implemented in v1",
                "reason": reason,
            },
        )

    # ─── MODE: refresh ────────────────────────────────────────────────────────
    if effective_mode == "refresh":
        # Future: re-init with same deployment_id
        return RuntimeEnvelope(
            tool="init_anchor",
            stage="000_INIT",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            payload={
                "ok": False,
                "error": "refresh mode not yet implemented in v1",
            },
        )

    # ─── Unknown mode ─────────────────────────────────────────────────────────
    return RuntimeEnvelope(
        tool="init_anchor",
        stage="000_INIT",
        status=RuntimeStatus.ERROR,
        verdict=Verdict.VOID,
        payload={
            "ok": False,
            "error": f"Unknown mode: {effective_mode}",
            "valid_modes": ["init", "state", "status", "revoke", "refresh"],
        },
    )


def _map_role(
    intent: Any | None,
    declared_name: str | None,
    payload: dict[str, Any] | None,
) -> str:
    """Map intent/declared_name to a role string."""
    if payload and payload.get("requested_role"):
        return payload["requested_role"]

    # Engineer if name suggests technical context
    if declared_name and any(
        k in str(declared_name).lower() for k in ["engineer", "architect", "dev", "coder"]
    ):
        return "engineer"

    # Auditor if contains audit/review keywords
    if declared_name and any(
        k in str(declared_name).lower() for k in ["audit", "review", "critic", "checker"]
    ):
        return "auditor"

    return "assistant"


def _v1_to_runtime_envelope(
    v1_result: Any,
    mode: str,
    dry_run: bool,
) -> RuntimeEnvelope:
    """Convert InitV1Envelope → RuntimeEnvelope for backward compat."""
    if not hasattr(v1_result, "to_dict"):
        # Already a dict
        result_dict = dict(v1_result)
        ok = result_dict.get("ok", False)
        return RuntimeEnvelope(
            tool="init_anchor",
            stage="000_INIT",
            status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
            verdict=Verdict.SEAL if ok else Verdict.VOID,
            allowed_next_tools=[],
            next_action=None,
            payload=result_dict,
        )

    v1_dict = v1_result.to_dict()
    ok = v1_dict.get("ok", False)
    status_str = v1_dict.get("status", "SUCCESS" if ok else "ERROR")

    # Map v1 risk_class to RiskClass enum
    risk_class_str = v1_dict.get("risk_class", "low")
    try:
        from arifosmcp.runtime.models import RiskClass

        risk_class = RiskClass(risk_class_str)
    except Exception:
        from arifosmcp.runtime.models import RiskClass

        risk_class = RiskClass.LOW

    return RuntimeEnvelope(
        tool="init_anchor",
        stage="000_INIT",
        status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
        verdict=Verdict.SEAL if ok else Verdict.VOID,
        allowed_next_tools=[],
        next_action=None,
        payload=v1_dict,
        risk_class=risk_class,
    )


def _error_envelope(message: str, mode: str) -> RuntimeEnvelope:
    return RuntimeEnvelope(
        tool="init_anchor",
        stage="000_INIT",
        status=RuntimeStatus.ERROR,
        verdict=Verdict.VOID,
        allowed_next_tools=[],
        next_action=None,
        payload={
            "ok": False,
            "error": message,
            "mode": mode,
        },
    )
