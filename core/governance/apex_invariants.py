"""
core/governance/apex_invariants.py — APEX Non-Learning Enforcement

This module codifies the hard constraint that APEX (Ψ/777-888) is a
CALCULATOR, not a LEARNER. These are constants of constitutional law,
not trainable parameters.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arifosmcp.core.physics.thermodynamics_hardened import LANDAUER_MIN


@dataclass(frozen=True)
class ApexConstants:
    """
    FROZEN constitutional constants.

    ⚠️  These are NOT trainable weights.
    ⚠️  These are NOT hyperparameters to tune.
    ⚠️  These are constants of governance law.

    Modification requires human legislative action (888_HOLD),
    not gradient descent or feedback loops.
    """

    # ═════════════════════════════════════════════════════════════════
    # F1-F13 FLOOR CONSTANTS (Hard Floors — Never Learnable)
    # ═════════════════════════════════════════════════════════════════

    # F2 Truth: Minimum veritas score
    F2_TRUTH_THRESHOLD: float = 0.99

    # F3 Tri-Witness: Minimum consensus score
    F3_TRI_WITNESS_MIN: float = 0.95

    # F4 Clarity: Maximum entropy increase (must reduce or conserve)
    F4_MAX_ENTROPY_DELTA: float = 0.0

    # F6 Empathy: Minimum care reliability
    F6_EMPATHY_MIN: float = 0.95

    # F7 Humility: Gödel Uncertainty Lock band
    F7_HUMILITY_MIN: float = 0.03
    F7_HUMILITY_MAX: float = 0.05

    # F8 Genius: Minimum wisdom index
    F8_GENIUS_MIN: float = 0.80

    # F9 Anti-Hantu: Maximum shadow cleverness
    F9_SHADOW_MAX: float = 0.30

    # F11 Auth: Identity tolerance (delta)
    F11_IDENTITY_TOLERANCE: float = 0.001

    # ═════════════════════════════════════════════════════════════════
    # THERMODYNAMIC CONSTANTS (Physics — Never Learnable)
    # ═════════════════════════════════════════════════════════════════

    # Landauer minimum energy per bit (Joules)
    LANDAUER_MIN: float = LANDAUER_MIN  # ~2.87×10^-21 J/bit

    # Minimum efficiency ratio (physical impossibility line)
    EFFICIENCY_MIN: float = 1.0

    # Suspicion threshold ("suspiciously cheap")
    EFFICIENCY_SUSPICION: float = 100.0

    # ═════════════════════════════════════════════════════════════════
    # VERDICT CONSTANTS (Enumerations — Never Learnable)
    # ═════════════════════════════════════════════════════════════════

    VERDICT_SEAL: str = "SEAL"
    VERDICT_VOID: str = "VOID"
    VERDICT_SABAR: str = "SABAR"
    VERDICT_HOLD: str = "888_HOLD"
    VERDICT_PARTIAL: str = "PARTIAL"


# Global singleton — immutable
APEX_CONSTANTS = ApexConstants()


def validate_apex_non_learning(obj: Any) -> dict[str, Any]:
    """
    Verify that an APEX-class object has no learning capabilities.

    This is a hard safety check: if someone accidentally adds learn(),
    fit(), train(), or update_thresholds() to an APEX class, this
    will catch it and raise an alarm.

    Args:
        obj: The object to validate (typically a prosecutor/judge class)

    Returns:
        Validation report with "clean" status and any violations found

    Example:
        >>> from arifosmcp.core.physics.thermodynamic_enforcement import ThermodynamicProsecutor
        >>> result = validate_apex_non_learning(ThermodynamicProsecutor)
        >>> assert result["clean"], f"APEX learning detected: {result['violations']}"
    """
    forbidden_methods = [
        "learn",
        "fit",
        "train",
        "update",
        "adapt",
        "tune",
        "optimize",
        "gradient",
        "backprop",
        "step",
        "epoch",
        "learn_from_feedback",
        "update_thresholds",
        "adjust_parameters",
    ]

    violations = []

    for method in forbidden_methods:
        if hasattr(obj, method):
            attr = getattr(obj, method)
            if callable(attr):
                violations.append(f"Forbidden learning method detected: {method}()")

    # Check for mutable threshold attributes (should be class-level constants)
    mutable_thresholds = []
    for attr_name in dir(obj):
        if not attr_name.startswith("_"):
            if any(x in attr_name.lower() for x in ["threshold", "ratio", "min", "max", "band"]):
                attr = getattr(obj, attr_name)
                if not isinstance(attr, (int, float, str, tuple, frozenset)):
                    if callable(attr):
                        continue  # Methods are checked above
                    mutable_thresholds.append(attr_name)

    return {
        "clean": len(violations) == 0,
        "violations": violations,
        "suspicious_attributes": mutable_thresholds,
        "object_type": type(obj).__name__,
        "message": (
            "✅ APEX object is clean — no learning capabilities detected"
            if len(violations) == 0
            else f"❌ APEX LEARNING VIOLATION: {len(violations)} forbidden methods found"
        ),
    }


def get_invariant_table() -> dict[str, dict[str, Any]]:
    """
    Return the complete APEX invariants table for documentation.

    This is used to generate the APEX_INVARIANTS.md documentation
    and for runtime validation that thresholds match specification.
    """
    return {
        "landauer_minimum": {
            "symbol": "E_min",
            "value": APEX_CONSTANTS.LANDAUER_MIN,
            "unit": "J/bit",
            "rationale": "Physics constant (F2 Truth)",
            "learnable": False,
        },
        "truth_threshold": {
            "symbol": "τ",
            "value": APEX_CONSTANTS.F2_TRUTH_THRESHOLD,
            "unit": "ratio",
            "rationale": "Hard floor for F2 Truth",
            "learnable": False,
        },
        "humility_band": {
            "symbol": "Ω₀",
            "value": [APEX_CONSTANTS.F7_HUMILITY_MIN, APEX_CONSTANTS.F7_HUMILITY_MAX],
            "unit": "uncertainty",
            "rationale": "Gödel Lock (F7 Humility)",
            "learnable": False,
        },
        "tri_witness_floor": {
            "symbol": "W₃",
            "value": APEX_CONSTANTS.F3_TRI_WITNESS_MIN,
            "unit": "consensus",
            "rationale": "Three-witness consensus (F3)",
            "learnable": False,
        },
        "genius_minimum": {
            "symbol": "G_min",
            "value": APEX_CONSTANTS.F8_GENIUS_MIN,
            "unit": "wisdom",
            "rationale": "F8 Genius floor",
            "learnable": False,
        },
        "shadow_ceiling": {
            "symbol": "C_dark_max",
            "value": APEX_CONSTANTS.F9_SHADOW_MAX,
            "unit": "deception",
            "rationale": "F9 Anti-Hantu",
            "learnable": False,
        },
        "empathy_minimum": {
            "symbol": "κᵣ_min",
            "value": APEX_CONSTANTS.F6_EMPATHY_MIN,
            "unit": "care",
            "rationale": "F6 Empathy (weakest stakeholder)",
            "learnable": False,
        },
        "efficiency_min": {
            "symbol": "η_min",
            "value": APEX_CONSTANTS.EFFICIENCY_MIN,
            "unit": "ratio",
            "rationale": "Physical impossibility line",
            "learnable": False,
        },
        "efficiency_suspicion": {
            "symbol": "η_s",
            "value": APEX_CONSTANTS.EFFICIENCY_SUSPICION,
            "unit": "ratio",
            "rationale": "Free lunch detector",
            "learnable": False,
        },
    }


__all__ = [
    "APEX_CONSTANTS",
    "ApexConstants",
    "validate_apex_non_learning",
    "get_invariant_table",
]
