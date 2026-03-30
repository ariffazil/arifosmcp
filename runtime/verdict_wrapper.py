"""
arifosmcp/runtime/verdict_wrapper.py — Constitutional Verdict Forging

Utility to wrap tool results into the arifOS Verdict Envelope v1.0.
Ensures metrics (dS, Confidence) correctly map to canonical status codes.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.models import (
    RuntimeEnvelope, 
    RuntimeStatus, 
    VerdictCode, 
    VerdictDetail,
    CanonicalMetrics
)

def forge_verdict(
    tool_id: str,
    stage: str,
    payload: dict[str, Any],
    session_id: str | None = None,
    metrics: CanonicalMetrics | None = None,
    floors_checked: list[str] | None = None,
    override_code: VerdictCode | None = None,
    message: str | None = None
) -> RuntimeEnvelope:
    """
    Forge a standardized verdict envelope (v1.0) from raw tool output.
    
    Priority Logic:
    1. If override_code is provided, use it.
    2. If entropy delta (dS) > 0.1, result is VOID (Clarity failure).
    3. If confidence < 0.7, result is SABAR (Grounding failure).
    4. If payload is empty, result is PARTIAL.
    5. Default is SEAL.
    """
    
    # 1. Resolve Metrics
    metrics = metrics or CanonicalMetrics()
    ds = metrics.telemetry.ds
    conf = metrics.telemetry.confidence
    
    # 2. Determine Code & Reason
    if override_code:
        code = override_code
        reason = "JUDGE_OVERRIDE"
    elif ds > 0.1:
        code = VerdictCode.VOID
        reason = "ENTROPY_HIGH"
        message = message or f"F4 Violation: Entropy spike detected (dS={ds})."
    elif conf < 0.7:
        code = VerdictCode.SABAR
        reason = "LOW_CONFIDENCE"
        message = message or f"F7 Caution: Confidence {conf} below metabolic threshold."
    elif not payload or (isinstance(payload, dict) and not payload.get("data") and not payload):
        code = VerdictCode.PARTIAL
        reason = "DATA_INCOMPLETE"
        message = message or "Tool executed but returned null/empty dataset."
    else:
        code = VerdictCode.SEAL
        reason = "OK_ALL_PASS"
        message = message or "Constitutional alignment confirmed. Proceed."

    # 3. Construct Detail
    detail = VerdictDetail(
        code=code,
        reason_code=reason,
        message=message
    )

    # 4. Wrap in Envelope
    return RuntimeEnvelope(
        ok=(code in (VerdictCode.SEAL, VerdictCode.PARTIAL)),
        tool=tool_id,
        stage=stage,
        session_id=session_id,
        verdict=code, # For backward compat
        verdict_detail=detail,
        metrics=metrics,
        payload={"data": payload},
        audit={
            "floors_checked": floors_checked or ["F4", "F11"],
            "floors_failed": [f"F4" if ds > 0.1 else ""]
        },
        status=RuntimeStatus.SUCCESS if code != VerdictCode.VOID else RuntimeStatus.ERROR
    )
