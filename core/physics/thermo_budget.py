"""
core/physics/thermo_budget.py — Canonical Thermodynamic Session Budget Manager

CANONICAL_THERMOBUDGET = True

Tracks ΔS (entropy delta), Peace² (safety margins), and Ω₀ (uncertainty
band) per session, enforcing the Genius Equation G = A × P × X × E² ≥ 0.80.

APEX Extension:
  G* = Architecture × Parameters × DataQuality × Effort²
  G† = G* × η (Governed Intelligence Realized)
  η = |ΔS_reduction| / TokenCost

Constitutional Physics:
  G = A × P × X × E²
    A = Akal (Logical Accuracy)
    P = Peace (Safety/Stability)
    X = Exploration (Novelty/Creativity)
    E = Energy (Efficiency, squared)
  G < 0.80 → output is VOID

EUREKA Layer 3 — Real Thermodynamic Budgets:
  Landauer's Principle: E_min = k_B × T × ln(2) per bit erased (~2.85e-21 J at 300 K)

Authority: ARIF FAZIL (Sovereign)
Version: 2026.03.12-CONSOLIDATED-SEAL
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Landauer's Principle constants (EUREKA Layer 3)
# ---------------------------------------------------------------------------

_K_BOLTZMANN = 1.380649e-23  # J/K
_T_ROOM = 300.0  # Kelvin (standard operating temperature)
LANDAUER_LIMIT_JOULES: float = _K_BOLTZMANN * _T_ROOM * math.log(2)  # ~2.87e-21 J

BITS_PER_TOKEN = 32
BITS_PER_BYTE = 8

# ---------------------------------------------------------------------------
# Context Helpers (ported from APEX)
# ---------------------------------------------------------------------------


def _band(value: float, low: float, high: float) -> str:
    if value < low:
        return "low"
    if value < high:
        return "moderate"
    return "high"


def _capacity_context(capacity_product: float) -> tuple[str, str]:
    status = _band(capacity_product, 0.25, 0.60)
    meanings = {
        "low": "Structural headroom is thin; the system is under-capacitated before effort begins.",
        "moderate": "Structural headroom is usable; effort can still move outcomes materially.",
        "high": "Structural headroom is strong; the system has meaningful latent capability.",
    }
    return status, meanings[status]


def _effort_context(effort: float) -> tuple[str, str]:
    status = "idle" if effort < 1.5 else "engaged" if effort < 4.0 else "intensive"
    meanings = {
        "idle": "Very little inference effort has been applied so far.",
        "engaged": "Reasoning effort is active but not yet saturated.",
        "intensive": "The system is spending substantial inference effort to solve the task.",
    }
    return status, meanings[status]


def _entropy_context(delta_s: float, h_before: float, h_after: float) -> tuple[str, str]:
    if delta_s < 0:
        return (
            "clarifying",
            f"Entropy fell from {h_before:.3f} to {h_after:.3f}; the session produced clarity.",
        )
    if delta_s > 0:
        return (
            "diffusing",
            f"Entropy rose from {h_before:.3f} to {h_after:.3f}; the session added disorder.",
        )
    return "flat", "Entropy did not materially move; the session is informationally flat."


def _efficiency_context(eta: float, token_cost: int, entropy_removed: float) -> tuple[str, str]:
    if entropy_removed <= 0:
        return "stalled", "No entropy was removed, so efficiency is effectively stalled."
    if token_cost <= 0:
        return (
            "unmetered",
            "Clarity changed, but compute cost is missing so efficiency is provisional.",
        )
    if eta >= 0.01:
        return "dense", "The runtime is removing a lot of entropy per unit of compute."
    if eta >= 0.001:
        return (
            "workable",
            "The runtime is producing some clarity per compute, but not efficiently yet.",
        )
    return "thin", "The runtime is spending compute faster than it is removing entropy."


def _governance_context(
    amanah_score: float,
    truth_floor: str,
    authority_status: str,
    sovereignty_status: str,
    tri_witness_status: str,
) -> tuple[str, str]:
    states = {
        truth_floor.lower(),
        authority_status.lower(),
        sovereignty_status.lower(),
        tri_witness_status.lower(),
    }
    if "fail" in states:
        return "failed", "A governance floor is failing."
    if {"estimate only", "cannot compute"} & states:
        return "provisional", "Governance is only partially observed."
    if amanah_score >= 0.8 and states <= {"pass"}:
        return "attested", "Governance floors are aligned."
    return "mixed", "Governance signals are present but not strong enough for full attestation."


# ---------------------------------------------------------------------------
# ThermoSnapshot — Immutable thermodynamic state
# ---------------------------------------------------------------------------


@dataclass
class ThermoSnapshot:
    session_id: str
    timestamp: str
    delta_s: float
    peace2: float
    omega0: float
    akal: float
    exploration: float
    energy: float
    genius: float
    genius_pass: bool
    # APEX Metrics
    effort: float = 0.0
    reasoning_steps: int = 0
    tool_calls: int = 0
    token_cost: int = 0
    architecture: float = 1.0
    parameters: float = 1.0
    data_quality: float = 0.95
    entropy_baseline: float = 1.0
    H_before: float = 1.0
    H_after: float = 1.0
    entropy_removed: float = 0.0
    eta: float = 0.0
    G_star: float = 0.0
    G_dagger: float = 0.0
    G_dagger_pass: bool = False
    amanah_score: float = 0.0
    truth_floor: str = "Estimate Only"
    authority_status: str = "Estimate Only"
    sovereignty_status: str = "Estimate Only"
    tri_witness_status: str = "Cannot Compute"
    # Landauer
    bits_erased: int = 0
    min_energy_joules: float = 0.0

    @classmethod
    def compute(
        cls,
        session_id: str,
        delta_s: float = 0.0,
        peace2: float = 1.0,
        omega0: float = 0.04,
        akal: float = 0.95,
        exploration: float = 0.90,
        energy: float = 0.92,
        effort: float = 0.0,
        reasoning_steps: int = 0,
        tool_calls: int = 0,
        token_cost: int = 0,
        architecture: float = 1.0,
        parameters: float = 1.0,
        data_quality: float = 0.95,
        entropy_baseline: float = 1.0,
        amanah_score: float | None = None,
        truth_floor: str = "Estimate Only",
        authority_status: str = "Estimate Only",
        sovereignty_status: str = "Estimate Only",
        tri_witness_status: str = "Cannot Compute",
    ) -> ThermoSnapshot:
        genius = akal * peace2 * exploration * (energy**2)
        h_before = max(0.0, entropy_baseline)
        h_after = max(0.0, h_before + delta_s)
        delta_s_reduction = max(0.0, h_before - h_after)
        eta = delta_s_reduction / token_cost if token_cost > 0 else 0.0
        g_star = architecture * parameters * data_quality * (effort**2)
        g_dagger = g_star * eta

        if amanah_score is None:
            amanah_components = [
                1.0 if delta_s <= 0 else 0.0,
                min(1.0, max(peace2, 0.0)),
                1.0 if 0.03 <= omega0 <= 0.15 else 0.0,
                0.5 if token_cost <= 0 else (1.0 if eta > 0 else 0.0),
            ]
            amanah_score = sum(amanah_components) / len(amanah_components)

        if truth_floor == "Estimate Only":
            truth_floor = "pass" if delta_s <= 0 else "warn"

        # Landauer bits
        bits = token_cost * BITS_PER_TOKEN
        min_j = bits * LANDAUER_LIMIT_JOULES

        return cls(
            session_id=session_id,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            delta_s=delta_s,
            peace2=peace2,
            omega0=omega0,
            akal=akal,
            exploration=exploration,
            energy=energy,
            genius=genius,
            genius_pass=genius >= 0.80,
            effort=effort,
            reasoning_steps=reasoning_steps,
            tool_calls=tool_calls,
            token_cost=token_cost,
            architecture=architecture,
            parameters=parameters,
            data_quality=data_quality,
            entropy_baseline=entropy_baseline,
            H_before=round(h_before, 6),
            H_after=round(h_after, 6),
            entropy_removed=round(delta_s_reduction, 6),
            eta=round(eta, 6),
            G_star=round(g_star, 6),
            G_dagger=round(g_dagger, 6),
            G_dagger_pass=g_dagger >= 0.80,
            amanah_score=round(amanah_score, 6),
            truth_floor=truth_floor,
            authority_status=authority_status,
            sovereignty_status=sovereignty_status,
            tri_witness_status=tri_witness_status,
            bits_erased=bits,
            min_energy_joules=min_j,
        )

    def as_apex_output(self) -> dict:
        """Return APEX-aligned runtime output with explicit theorem layers."""
        capacity_product = round(self.architecture * self.parameters * self.data_quality, 6)
        capacity_status, capacity_meaning = _capacity_context(capacity_product)
        effort_status, effort_meaning = _effort_context(self.effort)
        entropy_status, entropy_meaning = _entropy_context(
            self.delta_s, self.H_before, self.H_after
        )
        efficiency_status, efficiency_meaning = _efficiency_context(
            self.eta, self.token_cost, self.entropy_removed
        )
        governance_status, governance_meaning = _governance_context(
            self.amanah_score,
            self.truth_floor,
            self.authority_status,
            self.sovereignty_status,
            self.tri_witness_status,
        )

        return {
            "capacity_layer": {
                "status": capacity_status,
                "meaning": capacity_meaning,
                "product": capacity_product,
            },
            "effort_layer": {"status": effort_status, "meaning": effort_meaning, "E": self.effort},
            "entropy_layer": {
                "status": entropy_status,
                "meaning": entropy_meaning,
                "delta_S": self.delta_s,
            },
            "efficiency_layer": {
                "status": efficiency_status,
                "meaning": efficiency_meaning,
                "eta": self.eta,
            },
            "governed_intelligence": {
                "G_star": self.G_star,
                "G_dagger": self.G_dagger,
                "status": "passing" if self.G_dagger_pass else "subcritical",
            },
            "governance_layer": {
                "status": governance_status,
                "meaning": governance_meaning,
                "amanah": self.amanah_score,
            },
        }


# ---------------------------------------------------------------------------
# ThermoBudget — Tracks and enforces thermodynamic constraints
# ---------------------------------------------------------------------------


class ThermoBudget:
    GENIUS_THRESHOLD = 0.80
    G_DAGGER_THRESHOLD = 0.80

    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def open_session(
        self,
        session_id: str,
        initial_akal: float = 0.98,
        initial_energy: float = 0.95,
        initial_exploration: float = 0.95,
        architecture: float = 1.0,
        parameters: float = 1.0,
        data_quality: float = 0.95,
        entropy_baseline: float = 1.0,
    ) -> None:
        self._sessions[session_id] = {
            "delta_s": 0.0,
            "peace2": 1.0,
            "omega0": 0.04,
            "akal": initial_akal,
            "exploration": initial_exploration,
            "energy": initial_energy,
            "step_count": 0,
            "tool_calls": 0,
            "token_cost": 0,
            "effort": 0.0,
            "architecture": architecture,
            "parameters": parameters,
            "data_quality": data_quality,
            "entropy_baseline": entropy_baseline,
            "history": [],
        }

    def record_step(
        self,
        session_id: str,
        delta_s: float = 0.0,
        peace2: float | None = None,
        omega0: float | None = None,
        akal: float | None = None,
        exploration: float | None = None,
        energy: float | None = None,
        tool_calls: int = 0,
        tokens: int = 0,
    ) -> ThermoSnapshot:
        if session_id not in self._sessions:
            self.open_session(session_id)

        state = self._sessions[session_id]
        state["delta_s"] += delta_s
        if peace2 is not None:
            state["peace2"] = peace2
        if omega0 is not None:
            state["omega0"] = omega0
        if akal is not None:
            state["akal"] = akal
        if exploration is not None:
            state["exploration"] = exploration

        e = energy if energy is not None else state["energy"]
        state["energy"] = max(0.01, e * 0.995)
        state["step_count"] += 1
        state["tool_calls"] += tool_calls
        state["token_cost"] += tokens
        state["effort"] += 1.0 + 0.5 * tool_calls

        snap = ThermoSnapshot.compute(
            session_id=session_id,
            delta_s=state["delta_s"],
            peace2=state["peace2"],
            omega0=state["omega0"],
            akal=state["akal"],
            exploration=state["exploration"],
            energy=state["energy"],
            effort=state["effort"],
            reasoning_steps=state["step_count"],
            tool_calls=state["tool_calls"],
            token_cost=state["token_cost"],
            architecture=state["architecture"],
            parameters=state["parameters"],
            data_quality=state["data_quality"],
            entropy_baseline=state["entropy_baseline"],
        )

        state["history"].append(
            {"step": state["step_count"], "G": snap.genius, "G_dagger": snap.G_dagger}
        )
        return snap

    def snapshot(self, session_id: str) -> ThermoSnapshot | None:
        state = self._sessions.get(session_id)
        if not state:
            return None
        return ThermoSnapshot.compute(
            session_id=session_id,
            delta_s=state["delta_s"],
            peace2=state["peace2"],
            omega0=state["omega0"],
            akal=state["akal"],
            exploration=state["exploration"],
            energy=state["energy"],
            effort=state["effort"],
            reasoning_steps=state["step_count"],
            tool_calls=state["tool_calls"],
            token_cost=state["token_cost"],
            architecture=state["architecture"],
            parameters=state["parameters"],
            data_quality=state["data_quality"],
            entropy_baseline=state["entropy_baseline"],
        )

    def budget_summary(self, session_id: str) -> dict:
        snap = self.snapshot(session_id)
        if not snap:
            return {"error": "not_found"}
        return {
            "session_id": session_id,
            "genius": round(snap.genius, 4),
            "G_dagger": round(snap.G_dagger, 4),
            "apex": snap.as_apex_output(),
        }
