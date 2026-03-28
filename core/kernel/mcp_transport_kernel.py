"""Kernel-level response shaping for MCP transport adapters.

This module contains pure orchestration/output logic shared by transport layers.
It must not import MCP/HTTP/framework packages.
"""

from __future__ import annotations

import hashlib
from typing import Any

STAGE_777_EUREKA_FORGE = "777_EUREKA_FORGE"
STAGE_888_APEX_JUDGE = "888_APEX_JUDGE"


def compute_f12_level(injection_risk: float) -> int:
    """Convert injection risk score into a 0-3 floor level."""
    if injection_risk < 0.3:
        return 0
    if injection_risk < 0.6:
        return 1
    if injection_risk < 0.8:
        return 2
    return 3


def build_anchor_output(
    *,
    init_result: dict[str, Any],
    actor_id: str,
    platform: str,
    governance_mode: str = "HARD",
) -> dict[str, Any]:
    injection_risk = float(init_result.get("injection_risk", 0.0))
    return {
        "stage": "000",
        "session_id": init_result["session_id"],
        "actor_id": init_result.get("actor_id", actor_id),
        "platform": platform,
        "f12_score": injection_risk,
        "f12_matches": [],
        "f12_level": compute_f12_level(injection_risk),
        "governance_mode": governance_mode,
        "authority_token": init_result.get("authority", ""),
        "query_type": init_result.get("query_type", "UNKNOWN"),
    }


def build_reason_output(session_id: str, think_result: dict[str, Any]) -> dict[str, Any]:
    hypotheses_list = think_result.get("hypotheses", [])
    confidence_range = think_result.get("confidence_range", (0.8, 0.9))
    truth_score = confidence_range[0] if isinstance(confidence_range, (list, tuple)) else 0.8

    # FIX 1: Preserve QT Quad proof from organ output (no longer discarded)
    qt_proof = think_result.get("qt_proof", {})

    result = {
        "stage": "222_REASON",
        "session_id": session_id,
        "hypotheses_generated": len(hypotheses_list),
        "truth_score": truth_score,
        "clarity_delta": -0.2,
        "hypotheses": hypotheses_list,
        "confidence_range": confidence_range,
        "recommended_path": think_result.get("recommended_path"),
    }

    # FIX 1: Pass through qt_proof if present and complete
    if qt_proof:
        result["qt_proof"] = qt_proof
        # If QT Quad completed successfully, use its truth_score over legacy
        if qt_proof.get("complete") and "witnesses" in qt_proof:
            w_ai = qt_proof["witnesses"].get("w_ai", 0.0)
            if w_ai > 0:
                result["truth_score"] = max(truth_score, w_ai * 0.95)

    return result


def build_reason_error(
    *,
    session_id: str,
    hypotheses: int,
    truth_score_placeholder: float,
    clarity_delta_placeholder: float,
    error: Exception,
) -> dict[str, Any]:
    return {
        "verdict": "SABAR",
        "stage": "222_REASON",
        "session_id": session_id,
        "hypotheses_generated": hypotheses,
        "truth_score": truth_score_placeholder,
        "clarity_delta": clarity_delta_placeholder,
        "error": str(error),
    }


def build_integrate_output(
    *,
    session_id: str,
    reason_result: dict[str, Any],
    grounding: list | None,
    humility_omega_default: float,
) -> dict[str, Any]:
    tensor = reason_result.get("tensor")
    humility_omega = getattr(tensor, "humility", None)
    humility_omega_value = (
        humility_omega.omega_0 if humility_omega is not None else humility_omega_default
    )
    return {
        "verdict": "SEAL",
        "stage": "333_INTEGRATE",
        "session_id": session_id,
        "humility_omega": humility_omega_value,
        "grounding_sources": len(grounding) if grounding else 0,
        "knowledge_map": reason_result.get("knowledge_map", {}),
    }


def build_integrate_error(
    session_id: str, humility_omega_default: float, error: Exception
) -> dict[str, Any]:
    return {
        "verdict": "SABAR",
        "stage": "333_INTEGRATE",
        "session_id": session_id,
        "humility_omega": humility_omega_default,
        "error": str(error),
    }


def build_respond_output(
    session_id: str,
    stage_result: dict[str, Any],
    plan: str | None,
    plan_id: str | None = None,
) -> dict[str, Any]:
    output = {
        "verdict": "SEAL",
        "stage": "444_RESPOND",
        "session_id": session_id,
        "clarity_score": stage_result.get("clarity_score", 0.9),
        "output_length": len(plan) if plan else 0,
    }
    if plan_id:
        output["plan_id"] = plan_id
    return output


def build_respond_error(session_id: str, error: Exception) -> dict[str, Any]:
    return {
        "verdict": "SABAR",
        "stage": "444_RESPOND",
        "session_id": session_id,
        "clarity_score": 0.8,
        "error": str(error),
    }


def normalize_validate_result(
    result: dict[str, Any], stakeholders: list | None, default_kappa_r: float
) -> dict[str, Any]:
    output = dict(result)
    output["stakeholders_provided"] = stakeholders
    output.setdefault("verdict", "SEAL")
    output["stage"] = "555_VALIDATE"
    floor_scores = output.get("floor_scores", {})
    if isinstance(floor_scores, dict):
        output["peace_squared"] = floor_scores.get("f5_peace", 1.0)
        output["empathy_kappa_r"] = floor_scores.get(
            "f6_empathy", output.get("empathy_kappa_r", default_kappa_r)
        )
    elif hasattr(floor_scores, "f5_peace"):
        output["peace_squared"] = floor_scores.f5_peace
        output["empathy_kappa_r"] = floor_scores.f6_empathy
    return output


def build_validate_error(
    *,
    session_id: str,
    peace_squared_min: float,
    empathy_kappa_r_default: float,
    safe_default: bool,
    error: Exception,
) -> dict[str, Any]:
    return {
        "verdict": "SABAR",
        "stage": "555_VALIDATE",
        "session_id": session_id,
        "peace_squared": peace_squared_min,
        "empathy_kappa_r": empathy_kappa_r_default,
        "safe": safe_default,
        "error": str(error),
    }


def build_align_output(
    session_id: str, result: dict[str, Any], ethical_rules: list | None
) -> dict[str, Any]:
    return {
        "verdict": "SEAL",
        "stage": "666_ALIGN",
        "session_id": session_id,
        "alignment_score": result.get("alignment_score", 0.9),
        "rules_count": len(ethical_rules) if ethical_rules else 0,
    }


def build_align_error(session_id: str, error: Exception) -> dict[str, Any]:
    return {
        "verdict": "SABAR",
        "stage": "666_ALIGN",
        "session_id": session_id,
        "alignment_score": 0.8,
        "error": str(error),
    }


def build_forge_output(
    session_id: str, stage_result: dict[str, Any], implementation_details: dict[str, Any]
) -> dict[str, Any]:
    return {
        "verdict": "SEAL",
        "stage": STAGE_777_EUREKA_FORGE,
        "stage_legacy": "777_FORGE",
        "session_id": session_id,
        "code_fidelity": stage_result.get("fidelity", 0.95),
        "complexity_level": implementation_details.get("complexity", "standard"),
    }


def build_forge_error(session_id: str, error: Exception) -> dict[str, Any]:
    return {
        "verdict": "SABAR",
        "stage": STAGE_777_EUREKA_FORGE,
        "stage_legacy": "777_FORGE",
        "session_id": session_id,
        "code_fidelity": 0.9,
        "error": str(error),
    }


def normalize_audit_output(judge_dict: dict[str, Any], human_approve: bool) -> dict[str, Any]:
    output = dict(judge_dict)
    stage = str(output.get("stage", "")).upper()
    if stage in {"", "888", "888_AUDIT", "888_JUDGE"}:
        output["stage"] = STAGE_888_APEX_JUDGE
        if stage and stage != STAGE_888_APEX_JUDGE:
            output["stage_legacy"] = stage

    if output.get("verdict") == "888_HOLD" and human_approve:
        output["verdict"] = "SEAL"
        output["sovereign_ratified"] = True
    floor_scores = output.get("floor_scores", {})
    output["genius_G"] = (
        floor_scores.get("f8_genius", 0.0) if isinstance(floor_scores, dict) else 0.0
    )
    output["tri_witness_W3"] = (
        floor_scores.get("f3_tri_witness", 0.0) if isinstance(floor_scores, dict) else 0.0
    )
    return output


def build_audit_fallback(
    *,
    session_id: str,
    verdict: str,
    human_approve: bool,
    tri_witness_score: float,
) -> dict[str, Any]:
    final_verdict = "SEAL" if verdict == "888_HOLD" and human_approve else verdict
    return {
        "verdict": final_verdict,
        "stage": STAGE_888_APEX_JUDGE,
        "stage_legacy": "888_AUDIT",
        "session_id": session_id,
        "tri_witness_score": tri_witness_score,
        "genius_G": 0.85 if final_verdict == "SEAL" else 0.5,
    }


def build_audit_error(session_id: str, error: Exception) -> dict[str, Any]:
    return {"verdict": "SABAR", "error": f"Audit failed: {error}", "session_id": session_id}


def normalize_seal_receipt(session_id: str, receipt: Any) -> dict[str, Any]:
    if hasattr(receipt, "model_dump"):
        output = receipt.model_dump()
    elif isinstance(receipt, dict):
        output = dict(receipt)
    else:
        output = {"status": "SEALED"}
    output["stage"] = "999_SEAL"
    output["session_id"] = session_id
    status = output.get("status")
    if status == "SEALED":
        output["motto"] = "999 VAULT - Permanent"
    elif status == "SABAR":
        output["motto"] = "999 COOLING - Transient"
    else:
        output["motto"] = "999 TRANSIENT - Not Stored"
    return output


def build_legacy_seal(session_id: str, verdict: str) -> dict[str, Any]:
    seal_hash = hashlib.sha256(f"{session_id}:{verdict}".encode()).hexdigest()[:16]
    return {
        "verdict": "SEALED",
        "status": "SEALED",
        "stage": "999_SEAL",
        "session_id": session_id,
        "seal_id": f"SEAL-{seal_hash.upper()}",
        "motto": "999 END - Truth Cooled (Legacy)",
    }


def build_seal_error(session_id: str, error: Exception) -> dict[str, Any]:
    return {"verdict": "SABAR", "error": f"Seal failed: {error}", "session_id": session_id}
