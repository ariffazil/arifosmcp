"""
core/intelligence/w3.py — Tri-Witness (W3) Metric

W3 = (w_H · s_H  ×  w_A · s_A  ×  w_E · s_E) ^ (1/3)

Where:
  s_H = human_alignment_score  (0–1, default 1.0 if no human input yet)
  s_A = ai_confidence          (model-provided, must be explicit)
  s_E = earth_evidence_score   (avg EvidenceBundle quality scores)
  w_*  = weights               (default 1.0 each; Sovereign may override)

This is the geometric mean, not an arithmetic average.
Geometric mean prevents any single dominant witness from masking deficiencies.
A zero in any dimension collapses W3 to zero.

Verdict thresholds (F3 Tri-Witness, Mirror Floor):
  SEAL:     W3 ≥ 0.95
  PARTIAL:  W3 ≥ 0.75
  SABAR:    W3 ≥ 0.50 (refine and retry)
  888_HOLD: W3 < 0.50  OR  action is irreversible (F13 Sovereign mandate)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# THRESHOLDS
# ─────────────────────────────────────────────────────────────────────────────
W3_SEAL_THRESHOLD: float = 0.95
W3_PARTIAL_THRESHOLD: float = 0.75
W3_SABAR_THRESHOLD: float = 0.50

# Per-witness minimum floors (soft warning, not hard block)
W3_WITNESS_SOFT_FLOOR: float = 0.70


# ─────────────────────────────────────────────────────────────────────────────
# RESULT
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class W3Result:
    score: float                  # 0.0–1.0
    verdict: str                  # SEAL | PARTIAL | SABAR | 888_HOLD
    s_human: float = 1.0
    s_ai: float = 0.0
    s_earth: float = 0.0
    unstable_witnesses: list[str] = None  # which witnesses are below soft floor
    uncertainty: float = 0.0              # 1.0 - score (F7 Humility)

    def __post_init__(self):
        if self.unstable_witnesses is None:
            self.unstable_witnesses = []
        self.uncertainty = max(0.0, 1.0 - self.score)

    @property
    def is_seal(self) -> bool:
        return self.score >= W3_SEAL_THRESHOLD

    @property
    def confidence_band(self) -> tuple[float, float]:
        margin = 0.03
        return (max(0.0, self.score - margin), min(1.0, self.score + margin))


# ─────────────────────────────────────────────────────────────────────────────
# CORE COMPUTATION
# ─────────────────────────────────────────────────────────────────────────────
def compute_w3(
    s_human: float,
    s_ai: float,
    s_earth: float,
    w_human: float = 1.0,
    w_ai: float = 1.0,
    w_earth: float = 1.0,
    action_is_irreversible: bool = False,
) -> W3Result:
    """
    Compute the Tri-Witness score and derive the constitutional verdict.

    Args:
        s_human:               Human alignment score (0–1). Default 1.0 if no human in loop yet.
        s_ai:                  AI model confidence (0–1). Must be explicitly provided.
        s_earth:               Earth evidence quality score (0–1). From EvidenceBundle.quality_score avg.
        w_human/w_ai/w_earth:  Witness weights. Default equal (1.0). Sovereign can override via session_meta.
        action_is_irreversible: If True → 888_HOLD regardless of W3 (F13 Sovereign mandate).

    Returns:
        W3Result with score, verdict, and diagnostic breakdown.
    """
    # Clamp all inputs
    s_human = max(0.0, min(1.0, s_human))
    s_ai = max(0.0, min(1.0, s_ai))
    s_earth = max(0.0, min(1.0, s_earth))
    w_human = max(0.0, w_human)
    w_ai = max(0.0, w_ai)
    w_earth = max(0.0, w_earth)

    # Geometric mean
    product = (w_human * s_human) * (w_ai * s_ai) * (w_earth * s_earth)
    w3 = max(0.0, min(1.0, product ** (1.0 / 3.0))) if product > 0 else 0.0

    # Detect weak witnesses
    unstable = []
    if s_human < W3_WITNESS_SOFT_FLOOR:
        unstable.append(f"human_witness_weak ({s_human:.2f})")
    if s_ai < W3_WITNESS_SOFT_FLOOR:
        unstable.append(f"ai_confidence_below_threshold ({s_ai:.2f})")
    if s_earth < W3_WITNESS_SOFT_FLOOR:
        unstable.append(f"earth_evidence_weak ({s_earth:.2f})")

    # F13: irreversible actions always escalate to human
    if action_is_irreversible:
        logger.info("W3: F13 sovereign gate — action_is_irreversible=True → 888_HOLD (W3=%.3f)", w3)
        return W3Result(
            score=w3,
            verdict="888_HOLD",
            s_human=s_human, s_ai=s_ai, s_earth=s_earth,
            unstable_witnesses=unstable + ["F13_IRREVERSIBLE_PENDING"],
        )

    verdict = w3_to_verdict(w3)
    logger.debug(
        "W3=%.3f (H=%.2f A=%.2f E=%.2f) → %s",
        w3, s_human, s_ai, s_earth, verdict,
    )
    return W3Result(
        score=w3,
        verdict=verdict,
        s_human=s_human, s_ai=s_ai, s_earth=s_earth,
        unstable_witnesses=unstable,
    )


def w3_to_verdict(w3: float) -> str:
    """Map a raw W3 score to a constitutional verdict string."""
    if w3 >= W3_SEAL_THRESHOLD:
        return "SEAL"
    if w3 >= W3_PARTIAL_THRESHOLD:
        return "PARTIAL"
    if w3 >= W3_SABAR_THRESHOLD:
        return "SABAR"
    return "888_HOLD"


def compute_earth_score(bundles: list) -> float:
    """
    Compute the earth witness score from a list of EvidenceBundle objects.
    Returns average of bundle.quality_score values. Returns 0.0 for empty list.
    """
    if not bundles:
        return 0.0
    scores = [getattr(b, "quality_score", 0.5) for b in bundles]
    return sum(scores) / len(scores)


__all__ = [
    "W3Result",
    "W3_SEAL_THRESHOLD",
    "W3_PARTIAL_THRESHOLD",
    "W3_SABAR_THRESHOLD",
    "compute_w3",
    "w3_to_verdict",
    "compute_earth_score",
]
