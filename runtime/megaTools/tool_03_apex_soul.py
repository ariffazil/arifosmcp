"""
arifosmcp/runtime/megaTools/03_apex_soul.py

888_JUDGE: Final authority for verdicts and defense
Stage: 888_JUDGE | Trinity: PSI Ψ | Floors: F3, F12, F13

Modes: judge, rules, validate, hold, armor, notify, probe
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
from fastmcp.dependencies import CurrentContext


async def apex_soul(
    mode: str = "judge",
    payload: dict[str, Any] | None = None,
    proposal: str | None = None,
    execution_plan: dict | None = None,
    auth_context: dict | None = None,
    risk_tier: str = "medium",
    session_id: str | None = None,
    dry_run: bool = True,
    ctx: Any | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    resolved_payload = dict(payload or {})
    if proposal:
        resolved_payload.setdefault("proposal", proposal)
    if execution_plan:
        resolved_payload.setdefault("execution_plan", execution_plan)
    if auth_context:
        resolved_payload.setdefault("auth_context", auth_context)
    if risk_tier:
        resolved_payload.setdefault("risk_tier", risk_tier)
    if session_id:
        resolved_payload.setdefault("session_id", session_id)
    resolved_payload.setdefault("dry_run", dry_run)
    resolved_payload.update(kwargs)

    if "apex_soul" in HARDENED_DISPATCH_MAP:
        res = await HARDENED_DISPATCH_MAP["apex_soul"](mode=mode, payload=resolved_payload)
        if isinstance(res, dict):
            ok = res.get("ok", True)
            _payload = res.get("payload", res) if isinstance(res.get("payload"), dict) else res
            
            # ─── V2 FLATTENING ───
            if mode == "rules" and ok:
                # Move diagnostic fields to top level of payload for TestAuditRulesBootstrap
                _final_payload = {
                    "ok": True,
                    "tool": "apex_soul",
                    "status": "SUCCESS",
                    "result_type": "apex_rules_result@v2",
                    # Metadata for governance
                    "organ_stage": res.get("organ_stage", "888_JUDGE"),
                    "risk_tier": res.get("risk_tier", "low"),
                    "verdict": res.get("verdict", "SEAL"),
                    "g_score": res.get("g_score"),
                    "entropy": res.get("entropy"),
                }
                # Include all fields from inner payload (contracts, guidance, hooks)
                _final_payload.update({k: v for k, v in _payload.items() if v is not None})
                _payload = _final_payload

            # Ensure verdict is a valid Verdict Enum member
            verdict_val = res.get("verdict", "SEAL" if ok else "VOID")
            if isinstance(verdict_val, str):
                try:
                    effective_verdict = Verdict(verdict_val)
                except ValueError:
                    effective_verdict = Verdict.SEAL if ok else Verdict.VOID
            else:
                effective_verdict = verdict_val or (Verdict.SEAL if ok else Verdict.VOID)

            return RuntimeEnvelope(
                tool=res.get("tool", "apex_soul"),
                stage=res.get("organ_stage") or res.get("stage") or "888_JUDGE",
                status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
                verdict=effective_verdict,
                payload=_payload,
                session_id=res.get("session_id"),
            )
        return res

    # Fallback if dispatcher missing
    from arifosmcp.runtime.tools_internal import apex_soul_dispatch_impl
    return await apex_soul_dispatch_impl(
        mode=mode,
        payload=resolved_payload,
        auth_context=resolved_payload.get("auth_context", auth_context),
        risk_tier=resolved_payload.get("risk_tier", risk_tier),
        dry_run=bool(resolved_payload.get("dry_run", dry_run)),
        ctx=ctx or CurrentContext(),
    )
