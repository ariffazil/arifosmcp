"""
arifosmcp/runtime/megaTools/01_init_anchor.py

🔥 THE IGNITION STATE OF INTELLIGENCE (Unified)
Stage: 000_INIT | Trinity: PSI Ψ | Floors: F11, F12, F13

Modes: init, revoke, refresh, state, status
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP


async def init_anchor(
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
    deployment_id: str | None = None,
    session_class: str = "execute",
) -> RuntimeEnvelope:
    payload = dict(payload or {})
    if session_class:
        payload.setdefault("session_class", session_class)
    if human_approved is not None and human_approval is False:
        human_approval = human_approved
    if "human_approved" in payload and "human_approval" not in payload:
        payload["human_approval"] = payload.pop("human_approved")
    if raw_input:
        payload.setdefault("query", raw_input)
    if caller_context:
        payload.setdefault("caller_context", caller_context)
    if auth_context:
        payload.setdefault("auth_context", auth_context)
    if query:
        payload.setdefault("query", query)
    if raw_input:
        payload.setdefault("raw_input", raw_input)
    if session_id:
        payload.setdefault("session_id", session_id)
    if actor_id:
        payload.setdefault("actor_id", actor_id)
    if declared_name:
        payload.setdefault("declared_name", declared_name)
    if intent:
        payload.setdefault("intent", intent)
    if "human_approval" not in payload:
        payload["human_approval"] = human_approval
    if risk_tier:
        payload.setdefault("risk_tier", risk_tier)
    if raw_input:
        payload.setdefault("raw_input", raw_input)
    if pns_shield:
        payload.setdefault("pns_shield", pns_shield)
    if proof:
        payload.setdefault("proof", proof)
    if reason:
        payload.setdefault("reason", reason)
    payload.setdefault("use_memory", use_memory)
    payload.setdefault("use_heart", use_heart)
    payload.setdefault("use_critique", use_critique)
    if context:
        payload.setdefault("context", context)
    if model_soul:
        payload.setdefault("model_soul", model_soul)
    if deployment_id:
        payload.setdefault("deployment_id", deployment_id)

    if "init_anchor" in HARDENED_DISPATCH_MAP:
        if mode is None:
            mode = "init"
        res = await HARDENED_DISPATCH_MAP["init_anchor"](mode=mode, payload=payload)
        if isinstance(res, dict):
            ok = res.get("ok")
            if ok is None:
                ok = res.get("status") not in ("HOLD", "ERROR", "VOID", None)
            
            _next_tools = res.get("allowed_next_tools") or res.get("next_allowed_tools")
            if not _next_tools:
                _next_tools = [
                    "math_estimator",
                    "architect_registry",
                    "check_vital",
                    "init_anchor",
                ]
            
            _payload = res.get("payload", res) if isinstance(res.get("payload"), dict) else res
            
            # ─── V2 FLATTENING (Always return flat result for success) ───
            if ok:
                identity = _payload.get("identity") or {}
                bound_session = _payload.get("bound_session") or {}
                v2_result = {
                    "session_id": res.get("session_id"),
                    "resolved_session_id": res.get("session_id"),
                    "transport_session_id": payload.get("session_id") or "global",
                    "declared_actor_id": identity.get("declared_actor_id") or _payload.get("declared_name") or _payload.get("actor_id"),
                    "verified_actor_id": identity.get("verified_actor_id"),
                    "canonical_actor_id": identity.get("verified_actor_id") or identity.get("declared_actor_id") or _payload.get("actor_id") or "anonymous",
                    "auth_state": identity.get("auth_state", _payload.get("auth_state", "unverified")),
                    "base_identity": {
                        "declared": identity.get("declared_identity"),
                        "verified": identity.get("verified_identity"),
                        "verification_status": identity.get("verification_status", "unverified"),
                        "verification_source": identity.get("verification_source", "none"),
                    },
                    "self_claim_boundary": identity.get("self_claim_boundary"),
                    "bound_role": identity.get("bound_role") or bound_session.get("bound_role"),
                    "bound_session": bound_session,
                    "scope": _payload.get("scope"),
                    "continuation": _payload.get("continuation"),
                    "normalization": _payload.get("normalization"),
                    "challenge": _payload.get("challenge"),
                    "provenance": _payload.get("provenance"),
                    # Add diagnostic fields for backward compatibility in status/state modes
                    "bootstrap_sequence": _payload.get("bootstrap_sequence"),
                    "system_motto": _payload.get("system_motto"),
                    "caller_state": res.get("caller_state") or _payload.get("caller_state"),
                    # Stage 888 Diagnostics (Audit)
                    "tool_contract_table": _payload.get("tool_contract_table"),
                    "discovery_resource": _payload.get("discovery_resource"),
                    "floor_runtime_hooks": _payload.get("floor_runtime_hooks"),
                    "guidance": _payload.get("guidance"),
                    "message": _payload.get("message"),
                }
                
                # The final payload for the RuntimeEnvelope
                _final_payload = {
                    "ok": True,
                    "tool": "init_anchor",
                    "status": "SUCCESS",
                    "result_type": "init_anchor_result@v2",
                    "result": v2_result,
                    # Preserve governance metadata at top level
                    "organ_stage": res.get("organ_stage") or res.get("stage") or "000_INIT",
                    "risk_tier": res.get("risk_tier", "low"),
                    "verdict": res.get("verdict"),
                    "g_score": res.get("g_score"),
                    "entropy": res.get("entropy"),
                    "errors": res.get("errors", []),
                    "warnings": res.get("warnings", []),
                }
                # For backward compatibility with tests expecting keys in .payload
                _final_payload.update({k: v for k, v in v2_result.items() if v is not None})
                _payload = _final_payload

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
            # Ensure verdict is a valid Verdict Enum member
            verdict_val = res.get("verdict", "SEAL" if ok else "VOID")
            if isinstance(verdict_val, str):
                try:
                    effective_verdict = Verdict(verdict_val)
                except ValueError:
                    effective_verdict = Verdict.SEAL if ok else Verdict.VOID
            else:
                effective_verdict = verdict_val or (Verdict.SEAL if ok else Verdict.VOID)

            # Ensure valid defaults for Pydantic validation
            from arifosmcp.runtime.models import CanonicalAuthority, AuthorityLevel, ClaimStatus
            _authority = res.get("authority")
            if _authority is None:
                # Fallback authority if not provided by dispatcher
                _authority = CanonicalAuthority(
                    actor_id=res.get("actor_id") or res.get("declared_actor_id") or "anonymous",
                    level=AuthorityLevel.ANONYMOUS,
                    claim_status=ClaimStatus.ANONYMOUS
                )

            return RuntimeEnvelope(
                tool=res.get("tool", "init_anchor"),
                stage=res.get("organ_stage") or res.get("stage") or "000_INIT",
                status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
                verdict=effective_verdict,
                allowed_next_tools=_next_tools,
                next_action=_next_action,
                payload=_payload,
                session_id=res.get("session_id"),
                authority=_authority,
                auth_context=res.get("auth_context"),
                caller_state=res.get("caller_state") or "anonymous",
            )
        return res

    if mode is None:
        mode = "init"
    
    return RuntimeEnvelope(
        tool="init_anchor",
        stage="000_INIT",
        status=RuntimeStatus.ERROR,
        verdict=Verdict.VOID,
        payload={"error": "Hardened Dispatch Map missing init_anchor entry. System failure."},
    )
