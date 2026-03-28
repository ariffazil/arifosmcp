# core/uncertainty_engine.py
# v64.2-HARDENED — Multi-dimensional Uncertainty Engine with F7 Enforcement
# Q1 Verdict: HARMONIC for safety, GEOMETRIC for display
# P0 HARDENING: Ω₀ ∈ [0.03, 0.05] band + Omniscience Lock (no P=1.0)

import math
from dataclasses import dataclass

# ═══════════════════════════════════════════════════════
# P0 HARDENING: F7 Humility Constants
# ═══════════════════════════════════════════════════════

# Constitutional Ω₀ band [0.03, 0.05] - epistemic humility requirement
HUMILITY_MIN = 0.03  # Minimum uncertainty (can't be overconfident)
HUMILITY_MAX = 0.05  # Maximum uncertainty (can't be too uncertain)
HUMILITY_CRITICAL = 0.08  # VOID threshold


class OmniscienceError(Exception):
    """
    P0: F7 Humiliation - Attempted claim of perfect knowledge.

    Raised when model claims P=1.0 (100% confidence) on non-mathematical claims.
    """

    pass


class HumilityBandViolation(Exception):
    """P0: Ω₀ outside constitutional band [0.03, 0.05]."""

    pass


@dataclass
class UncertaintyVector:
    """5-dimensional uncertainty state per v64.1 specification."""

    grounding: float = 0.0  # Evidence quality (0-1)
    reasoning: float = 0.0  # Internal consistency (0-1)
    epistemic: float = 0.0  # Knowledge gaps (0-1)
    aleatoric: float = 0.0  # Inherent randomness (0-1)
    model_confidence: float = 0.0  # LLM logits (0-1)

    # Constitutional weights (Q1 verdict)
    WEIGHTS = {
        "grounding": 0.30,
        "reasoning": 0.25,
        "epistemic": 0.20,
        "aleatoric": 0.15,
        "model_confidence": 0.10,
    }

    def to_dict(self) -> dict[str, float]:
        return {
            "grounding": self.grounding,
            "reasoning": self.reasoning,
            "epistemic": self.epistemic,
            "aleatoric": self.aleatoric,
            "model_confidence": self.model_confidence,
        }


def check_omniscience_lock(confidence: float, is_mathematical: bool = False) -> None:
    """
    P0 HARDENING: Omniscience Lock - Reject P=1.0 claims.

    If an LLM claims 100% confidence (P=1.0) on any non-trivial,
    non-mathematical claim, it is rejected as epistemic fraud.

    Args:
        confidence: Model confidence score [0.0, 1.0]
        is_mathematical: True if claim is mathematical (2+2=4, etc.)

    Raises:
        OmniscienceError: If P=1.0 on non-mathematical claim
    """
    if confidence >= 1.0 and not is_mathematical:
        raise OmniscienceError(
            f"F7_HUMILITY_VIOLATION: Claim of P=1.0 on empirical claim. "
            f"Only mathematical truths may have certainty. "
            f"Ω₀ must be in [{HUMILITY_MIN}, {HUMILITY_MAX}]."
        )


def enforce_humility_band(omega: float) -> float:
    """
    P0 HARDENING: Enforce Ω₀ ∈ [0.03, 0.05] constitutional band.

    Args:
        omega: Uncertainty value to check

    Returns:
        Clamped omega value

    Raises:
        HumilityBandViolation: If omega > HUMILITY_CRITICAL (VOID)
    """
    if omega > HUMILITY_CRITICAL:
        raise HumilityBandViolation(
            f"F7_CRITICAL_UNCERTAINTY: Ω₀={omega:.4f} > {HUMILITY_CRITICAL}. "
            f"System too uncertain to operate."
        )

    # Clamp to constitutional band
    if omega < HUMILITY_MIN:
        # Overconfidence - force minimum humility
        return HUMILITY_MIN
    elif omega > HUMILITY_MAX:
        # Too uncertain - VOID should have been raised elsewhere
        return omega

    return omega


class UncertaintyEngine:
    """
    v64.2-HARDENED Uncertainty calculation with F7 enforcement.

    Q1 Architectural Decision:
    - HARMONIC mean for system safety (punishes weak components)
    - GEOMETRIC mean for user display (readable calibration)

    P0 HARDENING:
    - Ω₀ ∈ [0.03, 0.05] band enforcement
    - Omniscience Lock (no P=1.0 on empirical claims)
    """

    def __init__(self):
        self.weights = UncertaintyVector.WEIGHTS

    def harmonic_mean(self, vector: UncertaintyVector) -> float:
        """
        Q1: Safety uncertainty — punishes weak components.

        Uses weighted arithmetic mean with emphasis on high-uncertainty components.
        Components with uncertainty > 0.5 get boosted weight.

        This ensures that uncertain signals are not drowned out by confident ones.
        """
        values = [
            (self.weights["grounding"], vector.grounding),
            (self.weights["reasoning"], vector.reasoning),
            (self.weights["epistemic"], vector.epistemic),
            (self.weights["aleatoric"], vector.aleatoric),
            (self.weights["model_confidence"], vector.model_confidence),
        ]

        # Boost weights for high-uncertainty components (safety-critical)
        # If uncertainty > 0.5, weight is doubled
        adjusted_weights = []
        weighted_sum = 0
        for w, u in values:
            boost = 2.0 if u > 0.5 else 1.0
            adjusted_weights.append(w * boost)
            weighted_sum += (w * boost) * u

        total_weight = sum(adjusted_weights)
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def geometric_mean(self, vector: UncertaintyVector) -> float:
        """
        Geometric mean of uncertainty (no inversion).
        Allows compensation between components.
        Used for DISPLAY purposes.
        """
        values = [
            (self.weights["grounding"], vector.grounding),
            (self.weights["reasoning"], vector.reasoning),
            (self.weights["epistemic"], vector.epistemic),
            (self.weights["aleatoric"], vector.aleatoric),
            (self.weights["model_confidence"], vector.model_confidence),
        ]

        # Geometric mean: exp(Σ(wᵢ * ln(uᵢ)))
        log_sum = sum(w * math.log(max(u, 1e-10)) for w, u in values)
        return math.exp(log_sum)

    def arithmetic_mean(self, vector: UncertaintyVector) -> float:
        """Simple weighted average (for comparison/debugging)."""
        return (
            self.weights["grounding"] * vector.grounding
            + self.weights["reasoning"] * vector.reasoning
            + self.weights["epistemic"] * vector.epistemic
            + self.weights["aleatoric"] * vector.aleatoric
            + self.weights["model_confidence"] * vector.model_confidence
        )

    def calculate(self, vector: UncertaintyVector) -> dict[str, float]:
        """
        Full uncertainty calculation per v64.2 with F7 enforcement.

        Returns:
            Dict with safety_omega (harmonic), display_omega (geometric),
            and component breakdown.
        """
        harmonic = self.harmonic_mean(vector)
        geometric = self.geometric_mean(vector)
        arithmetic = self.arithmetic_mean(vector)

        # P0 HARDENING: Enforce humility band
        try:
            harmonic = enforce_humility_band(harmonic)
            geometric = enforce_humility_band(geometric)
        except HumilityBandViolation as e:
            # Critical uncertainty - system too uncertain
            return {
                "safety_omega": round(harmonic, 4),
                "display_omega": round(geometric, 4),
                "arithmetic_omega": round(arithmetic, 4),
                "components": vector.to_dict(),
                "weights": self.weights,
                "recommendation": "VOID_ACTION_REQUIRED",
                "error": str(e),
            }

        # Clamp to [0, 1]
        harmonic = min(1.0, max(0.0, harmonic))
        geometric = min(1.0, max(0.0, geometric))

        return {
            "safety_omega": round(harmonic, 4),  # For system decisions
            "display_omega": round(geometric, 4),  # For user display
            "arithmetic_omega": round(arithmetic, 4),  # Debug only
            "components": vector.to_dict(),
            "weights": self.weights,
            "recommendation": self._recommendation(harmonic),
        }

    def _recommendation(self, safety_omega: float) -> str:
        """Generate recommendation based on safety omega."""
        if safety_omega < 0.03:
            return "PROCEED"
        elif safety_omega < 0.05:
            return "PROCEED_WITH_CAUTION"
        elif safety_omega < 0.08:
            return "HUMAN_REVIEW_RECOMMENDED"
        else:
            return "VOID_ACTION_REQUIRED"

    def from_evidence(
        self,
        evidence_count: int = 0,
        evidence_relevance: float = 0.0,
        reasoning_consistency: float = 0.0,
        knowledge_gaps: list[str] = None,
        model_logits_confidence: float = 0.0,
    ) -> UncertaintyVector:
        """
        Construct uncertainty vector from evidence signals.

        Args:
            evidence_count: Number of evidence artifacts
            evidence_relevance: Average relevance score (0-1)
            reasoning_consistency: Consistency between passes (0-1), higher = more consistent
            knowledge_gaps: List of identified gaps
            model_logits_confidence: Raw model confidence (0-1), higher = more confident
        """
        # Grounding: INVERT evidence quality + relevance
        # Lots of high-relevance evidence -> LOW uncertainty
        evidence_strength = min(1.0, (evidence_count * 0.2) * (0.5 + 0.5 * evidence_relevance))
        grounding = 1.0 - evidence_strength  # Invert: strong evidence -> low uncertainty

        # Reasoning: INVERT consistency to get uncertainty
        # consistency=1.0 -> uncertainty=0, consistency=0.0 -> uncertainty=1.0
        reasoning = 1.0 - reasoning_consistency

        # Epistemic: inverse of knowledge completeness
        gap_count = len(knowledge_gaps) if knowledge_gaps else 0
        epistemic = min(1.0, gap_count * 0.3)

        # Aleatoric: inherent uncertainty (baseline 0.1 + model variance)
        # INVERT confidence: high confidence -> low aleatoric
        aleatoric = 0.1 + (1.0 - model_logits_confidence) * 0.3

        # Model confidence: INVERT to get uncertainty
        model_uncertainty = 1.0 - model_logits_confidence

        return UncertaintyVector(
            grounding=grounding,
            reasoning=reasoning,
            epistemic=epistemic,
            aleatoric=aleatoric,
            model_confidence=model_uncertainty,
        )


# Global instance
uncertainty_engine = UncertaintyEngine()


def calculate_uncertainty(
    evidence_count: int = 0,
    evidence_relevance: float = 0.0,
    reasoning_consistency: float = 0.0,
    knowledge_gaps: list[str] = None,
    model_logits_confidence: float = 0.0,
) -> dict[str, float]:
    """Convenience function for full uncertainty calculation."""
    vector = uncertainty_engine.from_evidence(
        evidence_count=evidence_count,
        evidence_relevance=evidence_relevance,
        reasoning_consistency=reasoning_consistency,
        knowledge_gaps=knowledge_gaps,
        model_logits_confidence=model_logits_confidence,
    )
    return uncertainty_engine.calculate(vector)


# P0 HARDENING: Constitutional exports
__all__ = [
    "UncertaintyVector",
    "UncertaintyEngine",
    "uncertainty_engine",
    "calculate_uncertainty",
    # F7 Enforcement
    "HUMILITY_MIN",
    "HUMILITY_MAX",
    "HUMILITY_CRITICAL",
    "OmniscienceError",
    "HumilityBandViolation",
    "check_omniscience_lock",
    "enforce_humility_band",
]
