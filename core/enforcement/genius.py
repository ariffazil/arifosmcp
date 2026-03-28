"""
core/enforcement/genius.py — Constitutional Genius & Dial Derivation

This module implements the "Real Scoring" system for arifOS.
It derives the 4 APEX Dials (A/P/X/E) from the 13 Constitutional Floors
via geometric projection (Eigendecomposition approximation).

G = A × P × X × E²

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.core.shared.floor_audit import AuditResult
from arifosmcp.core.shared.types import FloorScores

logger = logging.getLogger(__name__)

_FLOOR_ALIAS_MAP: dict[str, tuple[str, ...]] = {
    "f1_amanah": ("f1",),
    "f2_truth": ("f2", "truth_score", "akal"),
    "f3_tri_witness": ("f3",),
    "f4_clarity": ("f4", "clarity_score"),
    "f5_peace": ("f5", "peace2"),
    "f6_empathy": ("f6", "empathy_score", "kappa_r"),
    "f7_humility": ("f7", "omega_0", "omega0"),
    "f8_genius": ("f8", "g_prev", "G_prev", "genius_score"),
    "f9_anti_hantu": ("f9", "c_dark"),
    "f10_ontology": ("f10", "ontology_valid"),
    "f11_command_auth": ("f11", "command_auth"),
    "f12_injection": ("f12", "injection_risk"),
    "f13_sovereign": ("f13", "human_score", "sovereign_score"),
}
_BOOL_FLOORS = {"f10_ontology", "f11_command_auth"}
_FLOOR_DEFAULTS: dict[str, Any] = {
    "f1_amanah": 1.0,
    "f2_truth": 0.99,
    "f3_tri_witness": 0.95,
    "f4_clarity": 1.0,
    "f5_peace": 1.0,
    "f6_empathy": 0.95,
    "f7_humility": 0.04,
    "f8_genius": 0.80,
    "f9_anti_hantu": 0.0,
    "f10_ontology": True,
    "f11_command_auth": True,
    "f12_injection": 0.0,
    "f13_sovereign": 1.0,
}


class APEXDials(BaseModel):
    """
    The 4 APEX dials derived from floor scores.
    Each dial represents a dimension of constitutional compliance.
    """

    A: float = Field(ge=0.0, le=1.0, description="Akal: Mind/Clarity cluster (F2, F4, F7, F10)")
    P: float = Field(ge=0.0, le=1.0, description="Presence: Stability/Trust cluster (F1, F5, F11)")
    X: float = Field(
        ge=0.0, le=1.0, description="Exploration: Heart/Navigation cluster (F3, F6, F8_prev, F9)"
    )
    E: float = Field(
        ge=0.0, le=1.0, description="Energy: Vitality/Boundary cluster (F12, F13 + Budget)"
    )

    def to_dict(self) -> dict[str, float]:
        return {"A": self.A, "P": self.P, "X": self.X, "E": self.E}


def audit_result_to_floor_scores(audit_result: Any) -> FloorScores:
    """
    Convert a FloorAuditor AuditResult or a raw dict of results to a FloorScores object.
    """
    if isinstance(audit_result, AuditResult):
        results = audit_result.floor_results
    elif isinstance(audit_result, dict):
        # Could be a dict of FloorResult objects or a dict from build_governance_proof
        results = audit_result.get("floor_results", audit_result)
    else:
        return FloorScores()

    def get_score(fid: str, default: float = 1.0) -> float:
        res = results.get(fid)
        if hasattr(res, "score"):
            return res.score
        if isinstance(res, dict) and "score" in res:
            return res["score"]
        # Fallback for simple "pass"/"fail" strings
        if res == "pass":
            return 1.0
        if res == "fail":
            return 0.0
        return default

    def get_bool(fid: str, default: bool = True) -> bool:
        res = results.get(fid)
        if hasattr(res, "passed"):
            return res.passed
        if isinstance(res, dict) and "passed" in res:
            return res["passed"]
        if res == "pass":
            return True
        if res == "fail":
            return False
        return default

    return FloorScores(
        f1_amanah=get_score("F1"),
        f2_truth=get_score("F2", 0.99),
        f3_tri_witness=get_score("F3", 0.95),
        f4_clarity=get_score("F4", 1.0),
        f5_peace=get_score("F5", 1.0),
        f6_empathy=get_score("F6", 0.95),
        f7_humility=get_score("F7", 0.04),
        f8_genius=get_score("F8", 0.80),
        f9_anti_hantu=1.0 - get_score("F9", 1.0),
        f10_ontology=get_bool("F10"),
        f11_command_auth=get_bool("F11"),
        f12_injection=1.0 - get_score("F12", 1.0),
        f13_sovereign=get_score("F13"),
    )


def _first_present(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first present non-None value from a mapping."""
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _coerce_bool(value: Any, default: bool) -> bool:
    """Parse permissive bool-like values while preserving explicit false signals."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "pass", "approved", "seal"}:
            return True
        if lowered in {"false", "0", "no", "fail", "denied", "void"}:
            return False
    return bool(value)


def _coerce_float(value: Any, default: float) -> float:
    """Parse float-like values with stable defaults."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def coerce_floor_scores(
    source: FloorScores | AuditResult | dict[str, Any] | None = None,
    *,
    defaults: dict[str, Any] | None = None,
) -> FloorScores:
    """
    Canonicalize heterogeneous floor payloads into a single FloorScores object.

    This is the shared entrypoint for real APEX G measurement inputs.
    """
    if isinstance(source, FloorScores):
        return source
    if isinstance(source, AuditResult):
        return audit_result_to_floor_scores(source)
    if isinstance(source, dict) and "floor_results" in source:
        return audit_result_to_floor_scores(source)

    payload = source if isinstance(source, dict) else {}
    resolved_defaults = {**_FLOOR_DEFAULTS, **(defaults or {})}
    values: dict[str, Any] = {}

    for field_name, aliases in _FLOOR_ALIAS_MAP.items():
        value = _first_present(payload, (field_name, *aliases))
        default_value = resolved_defaults[field_name]
        if field_name in _BOOL_FLOORS:
            values[field_name] = _coerce_bool(value, bool(default_value))
        else:
            values[field_name] = _coerce_float(value, float(default_value))

    return FloorScores(**values)


def get_thermodynamic_budget_window(
    session_id: str,
    *,
    fallback_used: float = 0.5,
    fallback_max: float = 1.0,
) -> tuple[float, float]:
    """Resolve the real thermodynamic budget window, with explicit fallback."""
    try:
        from arifosmcp.core.physics.thermodynamics_hardened import get_thermodynamic_budget

        budget = get_thermodynamic_budget(session_id)
        return float(budget.consumed), float(budget.initial_budget)
    except Exception:
        return float(fallback_used), float(fallback_max)


def geometric_mean(values: list[float]) -> float:
    """
    Compute geometric mean of values.
    Returns 0.0 if any value is <= 0.0 to enforce HARD floor logic.
    """
    if not values:
        return 0.0

    # Constitutional Enforcement: If any floor is 0, the cluster is 0.
    if any(v <= 0 for v in values):
        return 0.0

    try:
        product = 1.0
        for v in values:
            product *= v
        return product ** (1.0 / len(values))
    except Exception as e:
        logger.error(f"Error calculating geometric mean: {e}")
        return 0.0


def floors_to_dials(
    floors: FloorScores,
    compute_budget_used: float = 0.5,
    compute_budget_max: float = 1.0,
    telemetry: dict[str, Any] | None = None,
) -> APEXDials:
    """
    Project 13 Floors + Telemetry onto 4 Dials (A/P/X/E).
    """
    # 1. Helper to convert bool floors to floats
    f10 = 1.0 if floors.f10_ontology else 0.0
    f11 = 1.0 if floors.f11_command_auth else 0.0

    # 2. A = AKAL (Mind/Structure)
    # P1 Strike: Akal = AI Confidence metric (F2) cluster
    f7_norm = (
        1.0
        if 0.03 <= floors.f7_humility <= 0.05
        else (1.0 - min(abs(floors.f7_humility - 0.04) * 10, 1.0))
    )

    akal = geometric_mean([floors.f2_truth, floors.f4_clarity, f7_norm, f10])

    # 3. P = PRESENCE (Stability/Trust)
    # P1 Strike: Present = Grounding/Truth score (F1, F5 cluster)
    presence_base = geometric_mean([floors.f1_amanah, floors.f5_peace, f11])

    # Temporal Dampening: P = P_base * Stability_t
    try:
        from arifosmcp.core.governance_kernel import get_governance_kernel
        kernel = get_governance_kernel()
        stability_t = kernel.temporal_stability
    except Exception:
        stability_t = 1.0

    presence = presence_base * stability_t

    # 4. X = EXPLORATION (Navigation/Heart)
    # P1 Strike: X uses W3 (Tri-Witness) and Exploration breadth
    anti_hantu_compliance = 1.0 - floors.f9_anti_hantu
    
    # Use the programmatic Tri-Witness consensus W3 = (H * A * E)^(1/3)
    w3 = floors.tri_witness_consensus
    
    # Incorporate exploration breadth if available in telemetry
    x_breadth = 1.0
    if telemetry and "exploration" in telemetry:
        # If we have a hypothesis count, use it to boost/dampen X
        hypotheses = telemetry["exploration"].get("hypotheses", [])
        if len(hypotheses) > 0:
            x_breadth = min(1.0, 0.5 + (len(hypotheses) * 0.1))

    exploration = (
        geometric_mean([w3, floors.f6_empathy, floors.f8_genius, anti_hantu_compliance]) * x_breadth
    )

    # 5. E = ENERGY (Vitality/Entropy)
    # P1 Strike: E cluster uses budget efficiency and uncertainty_score
    injection_compliance = 1.0 - floors.f12_injection
    energy_from_floors = geometric_mean([injection_compliance, floors.f13_sovereign])

    # Thermodynamic Efficiency
    energy_ratio = 1.0 - (compute_budget_used / max(compute_budget_max, 1e-6))
    energy_ratio = max(0.0, min(1.0, energy_ratio))
    
    # Uncertainty Dampening (Entropy)
    uncertainty_penalty = 0.0
    if telemetry and "entropy" in telemetry:
        uncertainty_penalty = float(telemetry["entropy"].get("uncertainty_score", 0.0))
    
    energy_vitality = (energy_from_floors + energy_ratio) / 2.0
    energy = max(0.0, energy_vitality - (uncertainty_penalty * 0.5))

    return APEXDials(A=akal, P=presence, X=exploration, E=energy)


def calculate_genius(
    floors: FloorScores,
    h: float = 0.0,
    compute_budget_used: float = 0.5,
    compute_budget_max: float = 1.0,
    telemetry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    The Unified Genius Equation: G = (A × P × X × E²) × (1 - h)
    """
    dials = floors_to_dials(floors, compute_budget_used, compute_budget_max, telemetry=telemetry)

    akal = dials.A
    presence = dials.P
    exploration = dials.X
    energy = dials.E

    # G = A * P * X * E^2 (APEX G Theorem)
    g_gen = akal * presence * exploration * (energy**2)
    final_g = g_gen * (1.0 - h)

    return {
        "genius_score": round(final_g, 4),
        "dials": dials.to_dict(),
        "hysteresis": h,
        "passed": final_g >= 0.80,
        "verdict": "SEAL" if final_g >= 0.80 else "PARTIAL" if final_g >= 0.60 else "VOID",
    }


__all__ = [
    "APEXDials",
    "audit_result_to_floor_scores",
    "calculate_genius",
    "coerce_floor_scores",
    "floors_to_dials",
    "get_thermodynamic_budget_window",
]
