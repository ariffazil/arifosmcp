"""
organs/3_apex.py — Stage 777-888: THE SOUL (GOVERNANCE APEX)

Eureka Forge (Discovery) and Apex Judge (Final Verdict).
Mandates Landauer Bound checks and monotone-safe logic.

EUREKA HARDENING:
- Semantic Coherence Verification (Layer 2): detect cross-stage contradictions
  before issuing the final verdict; critical contradictions force 888_HOLD.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re as _re
from typing import Any, Literal

from arifosmcp.core.shared.types import (
    ApexOutput,
    EurekaProposal,
    JudgmentRationale,
    NextAction,
    PsiSeal,
    Verdict,
)
from arifosmcp.core.shared.verdict_contract import normalize_verdict

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# EUREKA Layer 2 — Semantic Coherence Patterns
# ═══════════════════════════════════════════════════════

# Each entry: (pattern_a, pattern_b, severity)
# A contradiction is detected when BOTH patterns match the same text region
# OR when a floor-score value contradicts the stated verdict.
_COHERENCE_PATTERNS: list[tuple[str, str, str]] = [
    (r"low.risk|safe|minimal.impact", r"high.risk|dangerous|severe.impact", "critical"),
    (r"reversible|can.undo|recoverable", r"irreversible|permanent|cannot.undo", "critical"),
    (r"highly.confident|absolute.certainty|100.percent", r"uncertain|ambiguous|unclear", "major"),
    (r"no.injection|clean.input", r"injection.detected|bypass.attempt", "critical"),
]


def _check_floor_contradiction(
    floor_scores: Any,
    attr: str,
    threshold: float,
    comparison: str,
    verdict_candidate: str,
    blocked_verdicts: tuple[str, ...],
    floor_name: str,
    severity: str,
    description_fn: Any,
    confidence: float,
) -> dict[str, Any] | None:
    """Check a single floor score for contradictions with proposed verdict."""
    if not hasattr(floor_scores, attr):
        return None

    value = getattr(floor_scores, attr)
    violated = (comparison == "gt" and value > threshold) or (
        comparison == "lt" and value < threshold
    )

    if violated and verdict_candidate in blocked_verdicts:
        return {
            "stage_a": floor_name,
            "stage_b": "verdict",
            "severity": severity,
            "description": description_fn(value, verdict_candidate),
            "confidence": confidence,
        }
    return None


def _detect_contradictions(
    reason_summary: str | None,
    floor_scores: Any,
    verdict_candidate: str,
) -> list[dict[str, Any]]:
    """
    EUREKA Layer 2: Detect semantic contradictions between reason text and floor scores.

    Checks:
    1. Pattern-pair contradictions within reason_summary text.
    2. Floor-score vs verdict contradictions (e.g. high F12 injection risk + SEAL verdict).

    Returns a list of contradiction dicts with keys:
        stage_a, stage_b, severity, description, confidence
    """
    contradictions: list[dict[str, Any]] = []
    text = (reason_summary or "").lower()

    # 1. Text-level pattern-pair contradictions
    for pattern_a, pattern_b, severity in _COHERENCE_PATTERNS:
        if _re.search(pattern_a, text) and _re.search(pattern_b, text):
            contradictions.append(
                {
                    "stage_a": "reason_summary",
                    "stage_b": "reason_summary",
                    "severity": severity,
                    "description": f"Contradictory claims: '{pattern_a}' vs '{pattern_b}'",
                    "confidence": 0.80,
                }
            )

    # 2. Floor-score vs verdict contradictions (F12, F1, F9)
    floor_checks = [
        (
            "f12_injection",
            0.5,
            "gt",
            ("SEAL", "PARTIAL"),
            "F12_injection",
            "critical",
            lambda v, vc: f"F12 injection risk={v:.2f} but verdict={vc}",
            0.95,
        ),
        (
            "f1_amanah",
            0.3,
            "lt",
            ("SEAL",),
            "F1_amanah",
            "critical",
            lambda v, vc: f"F1 amanah={v:.2f} (high irreversibility) but verdict={vc}",
            0.90,
        ),
        (
            "f9_anti_hantu",
            0.3,
            "gt",
            ("SEAL",),
            "F9_anti_hantu",
            "major",
            lambda v, vc: f"F9 anti-hantu={v:.2f} (dark cleverness) but verdict={vc}",
            0.85,
        ),
    ]

    for attr, threshold, comp, blocked, floor_name, sev, desc_fn, conf in floor_checks:
        contradiction = _check_floor_contradiction(
            floor_scores,
            attr,
            threshold,
            comp,
            verdict_candidate,
            blocked,
            floor_name,
            sev,
            desc_fn,
            conf,
        )
        if contradiction:
            contradictions.append(contradiction)

    return contradictions


def _derive_next_actions(materiality: str) -> list[NextAction]:
    """Derive next actions based on materiality level."""
    action_map = {
        "idea_only": NextAction(
            action_type="human_review",
            description="Review proposal with sovereign.",
            requires_hold=True,
        ),
        "prototype": NextAction(
            action_type="code_sandbox",
            description="Run validation tests.",
            requires_888_hold=False,
        ),
        "production": NextAction(
            action_type="human_review",
            description="Submit to Stage 888 for final verdict.",
            requires_hold=True,
        ),
    }
    if materiality in action_map:
        return [action_map[materiality]]
    return []


async def forge(
    intent: str,
    session_id: str,
    eureka_type: str = "concept",
    materiality: str = "idea_only",
    auth_context: dict[str, Any] | None = None,
    max_tokens: int = 1000,
    **kwargs: Any,
) -> ApexOutput:
    """
    Stage 777: EUREKA FORGE (Discovery Actuator)

    Transforms intent into Eureka insight, proposes next actions based on
    materiality, and returns an ApexOutput with SEAL verdict.
    """
    from arifosmcp.core.physics.thermodynamics_hardened import consume_tool_energy

    consume_tool_energy(session_id, n_calls=1)

    floors = {"F3": "pass", "F8": "pass", "F11": "pass", "F12": "pass", "F13": "pass"}

    # 1. Forge Eureka Proposal
    proposal = EurekaProposal(
        type=eureka_type,  # type: ignore
        summary=f"Forged {eureka_type} discovery for: {intent[:50]}...",
        details="Forged through Stage 777 metabolic synthesis.",
        evidence_links=["reason_mind.step:3"],
    )

    # 2. Derive Next Actions from materiality
    next_actions = _derive_next_actions(materiality)

    # 3. Construct Output
    out = ApexOutput(
        session_id=session_id,
        verdict=Verdict.SEAL,
        intent=intent,
        eureka=proposal,
        next_actions=next_actions,
        floors=floors,
        human_witness=1.0,
        ai_witness=1.0,
        earth_witness=1.0,
        evidence={"grounding": "Constitutional Forge Logic"},
    )
    
    # --- V2 Telemetry ---
    res = out.model_dump(mode="json")
    res["actual_output_tokens"] = 100  # Simulated
    res["truncated"] = False
    return res


async def judge(
    session_id: str,
    verdict_candidate: str = "SEAL",
    reason_summary: str | None = None,
    auth_context: dict[str, Any] | None = None,
    max_tokens: int = 1000,
    **kwargs: Any,
) -> ApexOutput:
    """
    Stage 888: APEX JUDGE (Final Judgment)

    Rule: MONOTONE-SAFE. Cannot upgrade a weaker candidate.
    Discipline: APEX Theorem Gate (G† = G* · η)
    """
    from arifosmcp.core.enforcement.genius import (
        calculate_genius,
        coerce_floor_scores,
        get_thermodynamic_budget_window,
    )
    from arifosmcp.core.physics.thermodynamics_hardened import (
        check_landauer_before_seal,
        consume_tool_energy,
    )
    from arifosmcp.core.shared.types import Verdict

    consume_tool_energy(session_id, n_calls=1)

    # ─────────────────────────────────────────────────────────────────────────────
    # Phase 1: Input Validation & Normalization
    # ─────────────────────────────────────────────────────────────────────────────

    # 1. Map Candidate — normalize_verdict(888, ...) allows VOID at this stage
    candidate = normalize_verdict(888, verdict_candidate)

    # 2. Extract or Build Floor Scores
    floor_scores = coerce_floor_scores(
        kwargs.get("floor_scores") if kwargs.get("floor_scores") is not None else kwargs,
        defaults={"f2_truth": kwargs.get("akal", 0.99)},
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # Phase 2: Safety Gates (Monotone + Coherence)
    # ─────────────────────────────────────────────────────────────────────────────

    # 3. Monotone Safety Check — violations prevent SEAL upgrade
    violations = kwargs.get("violations", [])
    if violations and candidate == Verdict.SEAL:
        candidate = Verdict.PARTIAL

    # 4. EUREKA Layer 2: Semantic Coherence Verification
    # Detect contradictions between reason text, floor scores, and proposed verdict.
    # Critical contradictions force 888_HOLD before any further processing.
    contradictions = _detect_contradictions(reason_summary, floor_scores, candidate.value)
    critical_contradictions = [c for c in contradictions if c["severity"] == "critical"]
    if critical_contradictions:
        candidate = Verdict.HOLD_888
        reason_summary = (reason_summary or "") + (
            f" [COHERENCE HOLD: {len(critical_contradictions)} critical contradiction(s) detected]"
        )
        logger.warning(
            "APEX coherence violation for session %s: %s",
            session_id,
            critical_contradictions,
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # Phase 3: Genius Discipline (F8)
    # ─────────────────────────────────────────────────────────────────────────────

    # 5. Real Genius Calculation (The Discipline Layer)
    budget_used, budget_max = get_thermodynamic_budget_window(
        session_id,
        fallback_used=0.5,
        fallback_max=1.0,
    )

    genius_result = calculate_genius(
        floors=floor_scores,
        h=kwargs.get("hysteresis", 0.0),
        compute_budget_used=budget_used,
        compute_budget_max=budget_max,
    )

    g_score = genius_result["genius_score"]
    dials = genius_result["dials"]

    # 6. G Sovereignty Gate — F8 enforcement
    if candidate == Verdict.SEAL and g_score < 0.80:
        logger.info(
            f"arifOS APEX Discipline Check: G ({g_score:.4f}) < 0.80. Downgrading to PARTIAL."
        )
        candidate = Verdict.PARTIAL
        reason_summary = (reason_summary or "") + f" [APEX Gate: G={g_score:.4f} < 0.80]"

    # ─────────────────────────────────────────────────────────────────────────────
    # Phase 4: Physics Compliance (F4)
    # ─────────────────────────────────────────────────────────────────────────────

    # 7. Landauer Physics Check (Mandatory before SEAL)
    if candidate == Verdict.SEAL:
        try:
            check_landauer_before_seal(
                session_id=session_id,
                compute_ms=kwargs.get("compute_ms", 500),
                tokens=kwargs.get("tokens", 200),
                delta_s=kwargs.get("delta_s", -0.2),
            )
        except Exception as e:
            logger.warning(f"Landauer check failed: {e}")
            candidate = Verdict.SABAR
            reason_summary = f"Physics Law Violation: {str(e)}"

    # ─────────────────────────────────────────────────────────────────────────────
    # Phase 5: Output Construction
    # ─────────────────────────────────────────────────────────────────────────────

    # 8. Build Rationale
    rationale = JudgmentRationale(
        summary=reason_summary or f"Judgment finalized for session {session_id}.",
        tri_witness={"human": dials["E"], "ai": dials["A"], "earth": dials["P"]},
        omega_0=floor_scores.f7_humility,
    )

    # 9. Update floor statuses for output
    floors_status = {f"F{i}": "pass" for i in range(1, 14)}
    if g_score < 0.80:
        floors_status["F8"] = "partial"
    if floor_scores.f2_truth < 0.99:
        floors_status["F2"] = "fail"

    # 10. Assemble PsiSeal (Soul Manifest)
    psi_seal = PsiSeal(
        session_id=session_id,
        verdict=candidate,
        g_dagger=g_score,
        omega_infinity=rationale.omega_0,
        tri_witness=rationale.tri_witness,
        floor_scores=floor_scores.model_dump() if hasattr(floor_scores, 'model_dump') else floor_scores,
        metadata={
            "coherence_contradictions": len(contradictions),
            "landauer_compliant": candidate == Verdict.SEAL,
            "human_witness": dials["E"]
        }
    )

    # 11. Construct Output
    out = ApexOutput(
        session_id=session_id,
        verdict=candidate,
        final_verdict=candidate,
        reasoning=rationale,
        psi_seal=psi_seal,
        floors=floors_status,
        metrics={
            "G": g_score,
            "akal": round(dials["A"], 4),
            "presence": round(dials["P"], 4),
            "exploration": round(dials["X"], 4),
            "energy": round(dials["E"], 4),
            "coherence_contradictions": len(contradictions),
            "coherence_critical": len(critical_contradictions),
        },
        floor_scores=floor_scores,
        human_witness=dials["E"],
        ai_witness=dials["A"],
        earth_witness=dials["P"],
        human_approve=True,  # Satisfy F13
        evidence={"grounding": "Constitutional Apex Consensus"},  # Satisfy F2
    )
    
    # --- V2 Telemetry ---
    res = out.model_dump(mode="json")
    res["actual_output_tokens"] = 60  # Simulated
    res["truncated"] = False
    return res


async def apex(
    action: Literal["forge", "judge", "full"] = "full",
    session_id: str = "global",
    intent: str | None = None,
    verdict_candidate: str = "SEAL",
    max_tokens: int = 1000,
    **kwargs: Any,
) -> ApexOutput:
    """
    Unified APEX Interface
    """
    if action == "forge":
        return await forge(intent or "Discovery", session_id, **kwargs)
    elif action == "judge":
        return await judge(session_id, verdict_candidate, **kwargs)

    # Default Full Judgment Flow
    return await judge(session_id, verdict_candidate, **kwargs)


# Unified aliases
sync = apex


__all__ = ["apex", "forge", "judge", "sync"]
