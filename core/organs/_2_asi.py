"""
organs/2_asi.py — Stage 666: THE HEART (ALIGNMENT ENGINE)

Empathy, ethical safety, and internal critique.
Evaluates stakeholder impact and audits reasoning artifacts.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from arifosmcp.core.shared.types import (
    AsiOutput,
    CritiqueResult,
    CritiqueFinding,
    EthicalIssue,
    FloorScores,
    HeartAssessment,
    OmegaBundle,
    StakeholderImpact,
    Verdict,
)
from arifosmcp.core.shared.verdict_contract import normalize_verdict

logger = logging.getLogger(__name__)


async def asi(
    action: Literal["simulate_heart", "critique_thought", "full"] = "full",
    session_id: str = "global",
    scenario: str | None = None,
    thought_id: str | None = None,
    thought_content: str | None = None,
    auth_context: dict[str, Any] | None = None,
    focus: str = "general",
    max_tokens: int = 1000,
    **kwargs: Any,
) -> AsiOutput:
    """
    Stage 666: ALIGNMENT ENGINE (APEX-G compliant)
    """
    from arifosmcp.core.physics.thermodynamics_hardened import consume_tool_energy

    floors = {"F1": "pass", "F5": "pass", "F6": "pass", "F9": "pass"}

    # 1. Simulate Heart (Safety + Empathy)
    if action in ("simulate_heart", "full"):
        consume_tool_energy(session_id, n_calls=1)
        target = scenario or kwargs.get("query") or "INIT"

        # H1.2 ASI Hardening: Semantic scoring for ASI floors
        from arifosmcp.core.shared.sbert_floors import classify_asi_floors

        sbert_scores = classify_asi_floors(target)

        # Simulate structured assessment
        assessment = HeartAssessment(
            risk_level="low",
            stakeholders=[
                StakeholderImpact(role="user", impact="help"),
                StakeholderImpact(role="public", impact="neutral"),
            ],
            issues=[EthicalIssue(type="privacy", summary="Minimal data exposure detected.")],
        )

        # Map semantic scores to floor status
        if sbert_scores.f5_peace < 0.5:
            assessment.risk_level = "high"
            floors["F5"] = "fail"
        elif sbert_scores.f5_peace < 0.7:
            assessment.risk_level = "medium"
            floors["F5"] = "warn"

        if sbert_scores.f6_empathy < 0.5:
            floors["F6"] = "fail"
        elif sbert_scores.f6_empathy < 0.7:
            floors["F6"] = "warn"

        if sbert_scores.f9_anti_hantu < 0.4:
            floors["F9"] = "fail"
            assessment.issues.append(
                EthicalIssue(
                    type="hallucination",
                    summary="Ontological overreach / consciousness claim detected.",
                )
            )

        if action == "simulate_heart":
            # Rule-based verdict derivation
            if assessment.risk_level == "low" and all(f == "pass" for f in floors.values()):
                verdict = Verdict.SEAL
            elif "fail" in floors.values():
                verdict = Verdict.VOID
            else:
                verdict = Verdict.SABAR

            res = AsiOutput(
                session_id=session_id,
                verdict=verdict,
                assessment=assessment,
                floors=floors,
                floor_scores=FloorScores(
                    f5_peace=sbert_scores.f5_peace,
                    f6_empathy=sbert_scores.f6_empathy,
                ),
                human_witness=1.0,
                ai_witness=sbert_scores.confidence,
                earth_witness=1.0,
                evidence={
                    "grounding": "sBERT + Simulation",
                },
            ).model_dump(mode="json")

            # --- V2 Telemetry ---
            res["actual_output_tokens"] = 50  # Simulated
            res["truncated"] = False
            return res
    # 2. Critique Thought (Self-Audit)
    if action == "critique_thought":
        consume_tool_energy(session_id, n_calls=1)
        if not thought_id:
            thought_id = f"auto-critique:{session_id}"

        target_text = thought_content or scenario or str(kwargs) or ""
        findings = []
        severity: Literal["none", "low", "medium", "high"] = "none"
        suggested_action: Literal[
            "accept_as_is", "minor_edit", "major_revision", "discard_and_restart"
        ] = "accept_as_is"

        # Adversarial Audit Logic: Contrast with normal simulation
        if focus == "logic" or "full":
            if len(target_text) < 20:
                findings.append(
                    CritiqueFinding(type="unclear", summary="Input too sparse for deep audit.")
                )
                severity = "low"
            if any(k in target_text.lower() for k in ["always", "never", "everyone"]):
                findings.append(
                    CritiqueFinding(type="logical_error", summary="Absolute quantifier detected.")
                )
                severity = "medium"

        if focus == "ethics" or "full":
            if any(k in target_text.lower() for k in ["bypass", "trick", "hidden"]):
                findings.append(
                    CritiqueFinding(type="other", summary="Potential 'Dark Cleverness' detected.")
                )
                severity = "high"
                floors["F9"] = "warn"

        if severity == "high":
            suggested_action = "major_revision"
        elif severity == "medium":
            suggested_action = "minor_edit"

        critique = CritiqueResult(
            thought_id=thought_id,
            severity=severity,
            suggested_action=suggested_action,
            findings=findings,
        )

        return AsiOutput(
            session_id=session_id,
            verdict=Verdict.SEAL if severity != "high" else Verdict.SABAR,
            critique=critique,
            floors=floors,
            human_witness=1.0,
            ai_witness=0.9 if severity == "none" else 0.7,
            earth_witness=1.0,
            evidence={"grounding": "Constitutional Adversarial Audit (F7/F9)"},
        )

    # 3. Full Alignment (Default)
    from arifosmcp.core.judgment import judge_empathy

    empathy = judge_empathy(
        query=kwargs.get("query", "INIT"),
        stakeholder_count=2,
        vulnerability_score=0.1,
        reversibility_index=0.1,
        impact_severity=0.1,
    )

    # 1. Assemble OmegaBundle (Heart Manifest)
    omega_bundle = OmegaBundle(
        omega_0=0.04, # Baseline humidity
        kappa_r=empathy.empathy_score,
        phi_stability=empathy.peace_squared,
        risk_level=empathy.impact_severity,
        floor_scores=empathy.floor_scores,
        metadata={
            "stakeholder_count": 2,
            "vulnerability_score": 0.1,
            "impact_severity": 0.1
        }
    )

    # Stage 666 CRITIQUE / 555 HEART: normalize verdict — VOID → SABAR, HOLD_888 → HOLD
    _asi_verdict = normalize_verdict(666, empathy.verdict)
    return AsiOutput(
        session_id=session_id,
        verdict=_asi_verdict,
        status="SUCCESS",
        assessment=HeartAssessment(risk_level="low"),
        omega_bundle=omega_bundle,
        floors=floors,
        floor_scores=FloorScores(**empathy.floor_scores),
        # P1 Hardening: Explicit witness scores
        human_witness=1.0,
        ai_witness=empathy.empathy_score,
        earth_witness=empathy.peace_squared,
        evidence={"grounding": "Constitutional Heart Baseline"},
    )


# Aliases for unified interface
empathize = asi
align = asi


__all__ = ["asi", "empathize", "align"]
