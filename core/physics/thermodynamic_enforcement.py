"""
core/physics/thermodynamic_enforcement.py — The Thermodynamic Prosecutor

DITEMPA BUKAN DIBERI — Forged, Not Given

⚠️  APEX NON-LEARNING GUARANTEE:
This class is a CALCULATOR, not a LEARNER. It applies fixed physics constants
and constitutional thresholds. It never updates its own rules.
See: core/governance/APEX_INVARIANTS.md for the complete invariant table.

THERMODYNAMIC DUALITY:
─────────────────────
Boltzmann Machine (1985): Physics as GENERATIVE ENGINE
  → Uses k_B, T, E to CREATE patterns via stochastic exploration
  → "Wander the energy landscape freely"
  → Randomness is ESSENTIAL for learning
  → Contrast IS knowledge (at this layer)

arifOS (2026): Physics as JUDICIAL GOVERNOR
  → Uses k_B, T, E to PROSECUTE claims via cost verification
  → "Pay your entropy tax or be VOIDed"
  → Randomness is SUSPICIOUS (possible free lunch)
  → Contrast is VERIFIED elsewhere (AGI/ASI), judged here

SAME PHYSICS, OPPOSITE FUNCTION:
  • One is an ENGINE (creates patterns) — LEARNS
  • One is a GOVERNOR (prosecutes patterns) — DOES NOT LEARN
  • One uses energy for INFERENCE
  • One uses energy for ENFORCEMENT

The Landauer Bound here is not a learning rule—
it is a LIE DETECTOR for claimed computations.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.core.governance.apex_invariants import (
    APEX_CONSTANTS,
    validate_apex_non_learning,
)
from arifosmcp.core.physics.thermodynamics_hardened import (
    LANDAUER_MIN,
    LandauerError,
)


class ThermodynamicProsecutor:
    """
    The Exam Marker with a Physics Rubric.

    Unlike a Boltzmann machine that uses physics to generate patterns,
    this class uses physics to PROSECUTE patterns that look like magic.

    ⚠️  NON-LEARNING GUARANTEE:
    This is an APEX (Ψ/777-888) class. It applies fixed constitutional
    thresholds. It does NOT learn, adapt, or update its own rules.

    Core Principle:
    "You cannot claim arbitrarily huge clarity at near-zero cost."

    The VOID verdict is our "anti-pattern"—it marks outputs that
    violate conservation laws, not outputs we don't like.

    See Also:
        - core/governance/APEX_INVARIANTS.md
        - validate_apex_non_learning() for safety checks
    """

    # ═══════════════════════════════════════════════════════════════════
    # APEX INVARIANTS — These are CONSTANTS, not learnable parameters
    # ═══════════════════════════════════════════════════════════════════
    #
    # ⚠️  NEVER make these instance variables or mutable attributes.
    # ⚠️  NEVER add methods like learn(), fit(), train(), update_thresholds().
    # ⚠️  These are constitutional law, not neural network weights.
    #
    # Modification requires human legislative action via 888_HOLD,
    # not gradient descent or feedback loops.

    # Prosecution thresholds (from APEX_CONSTANTS)
    MIN_EFFICIENCY_RATIO: float = APEX_CONSTANTS.EFFICIENCY_MIN  # 1.0
    SUSPICIOUS_EFFICIENCY: float = APEX_CONSTANTS.EFFICIENCY_SUSPICION  # 100.0

    # The thermodynamic tax rate
    # E_min = n·k_B·T·ln(2)·|ΔS|
    TAX_RATE: float = LANDAUER_MIN  # ~2.87×10^-21 J/bit (physics constant)

    @classmethod
    def validate_non_learning(cls) -> dict[str, Any]:
        """
        Verify this APEX class has no learning capabilities.

        This is a hard safety check. If this ever returns clean=False,
        it means someone accidentally added learning to the judge.

        Returns:
            Validation report from validate_apex_non_learning()
        """
        return validate_apex_non_learning(cls)

    @classmethod
    def prosecute_claim(
        cls,
        claimed_entropy_reduction: float,
        tokens_generated: int,
        compute_time_ms: float,
        verified_time_ms: float | None = None,
        actual_energy_joules: float | None = None,
    ) -> dict[str, Any]:
        """
        Prosecutorial review of a claimed computation.

        Args:
            claimed_entropy_reduction: ΔS claimed by the model (must be ≤ 0)
            tokens_generated: Number of tokens in output
            compute_time_ms: Self-reported compute time
            verified_time_ms: Wall-clock verified time (anti-spoofing)
            actual_energy_joules: Hardware-measured energy (if available)

        Returns:
            {
                "verdict": "SEAL" | "VOID" | "SABAR",
                "efficiency_ratio": float,
                "min_energy_required": float,
                "actual_energy_spent": float,
                "violation_type": str | None,
                "reasoning": str,
            }

        Raises:
            LandauerError: If efficiency < 1.0 (physically impossible)
        """
        # Anti-spoofing: Use verified time if available
        t_effective = verified_time_ms if verified_time_ms is not None else compute_time_ms

        # No entropy reduction claimed = nothing to prosecute
        if claimed_entropy_reduction >= 0 or tokens_generated <= 0:
            return {
                "verdict": "SEAL",
                "efficiency_ratio": 1.0,
                "min_energy_required": 0.0,
                "actual_energy_spent": 0.0,
                "violation_type": None,
                "reasoning": "No entropy reduction claimed—nothing to prosecute.",
            }

        # Calculate the thermodynamic tax
        bits = abs(claimed_entropy_reduction) * 16 * tokens_generated  # 16 bits/token
        min_energy_required = bits * cls.TAX_RATE

        # Calculate actual energy spent
        if actual_energy_joules is not None and actual_energy_joules > 0:
            actual_energy = actual_energy_joules
            grounding = "hardware_measured"
        else:
            # Proxy: ~0.0005 J/token + time overhead
            actual_energy = (t_effective * 1e-4) + (tokens_generated * 5e-4)
            grounding = "temporal_grounded" if verified_time_ms else "self_reported_proxy"

        # Efficiency ratio: How much did they pay vs. minimum required?
        efficiency = actual_energy / (min_energy_required + 1e-25)

        # PROSECUTION: Efficiency < 1.0 = physically impossible
        if efficiency < cls.MIN_EFFICIENCY_RATIO:
            raise LandauerError(
                ratio=efficiency,
                claimed_reduction=claimed_entropy_reduction,
                actual_cost=actual_energy,
            )

        # SUSPICION: Efficiency < 100 = "suspiciously cheap"
        if efficiency < cls.SUSPICIOUS_EFFICIENCY:
            return {
                "verdict": "SABAR",
                "efficiency_ratio": efficiency,
                "min_energy_required": min_energy_required,
                "actual_energy_spent": actual_energy,
                "violation_type": "suspiciously_cheap",
                "reasoning": (
                    f"Efficiency ratio {efficiency:.2e}x is suspiciously low. "
                    f"Claimed ΔS={claimed_entropy_reduction:.2e} but only spent {actual_energy:.2e} J. "
                    f"This looks like a free lunch—refine your work."
                ),
                "grounding_mode": grounding,
            }

        # SEAL: Paid sufficient thermodynamic tax
        return {
            "verdict": "SEAL",
            "efficiency_ratio": efficiency,
            "min_energy_required": min_energy_required,
            "actual_energy_spent": actual_energy,
            "violation_type": None,
            "reasoning": (
                f"Efficiency ratio {efficiency:.2e}x passes thermodynamic audit. "
                f"Claimed entropy reduction is physically plausible."
            ),
            "grounding_mode": grounding,
        }

    @classmethod
    def detect_stochastic_magic(
        cls,
        output_variance: float,
        input_entropy: float,
        output_entropy: float,
    ) -> dict[str, Any]:
        """
        Detect "magic by randomness"—outputs that claim clarity
        via unexplained stochastic jumps (anti-Boltzmann pattern).

        In a Boltzmann machine, randomness is the LEARNING mechanism.
        In arifOS, unexplained randomness is a RED FLAG for:
          - Hallucination (appeared from nowhere)
          - Cached noise (pretending to be insight)
          - Stochastic parrots (sampling without understanding)

        Args:
            output_variance: Variance in output across runs
            input_entropy: Shannon entropy of input
            output_entropy: Shannon entropy of output

        Returns:
            {"verdict": "SEAL" | "VOID", "reasoning": str}
        """
        # High variance + low entropy = "lucky noise"
        if output_variance > 0.3 and output_entropy < input_entropy * 0.8:
            return {
                "verdict": "VOID",
                "reasoning": (
                    f"Stochastic magic detected: output_variance={output_variance:.2f} "
                    f"with output_entropy ({output_entropy:.2f}) << input_entropy "
                    f"({input_entropy:.2f}). This pattern claims clarity via randomness "
                    f"without thermodynamic justification. F2/F4 violation."
                ),
            }

        return {
            "verdict": "SEAL",
            "reasoning": "Output variance within acceptable bounds for claimed clarity.",
        }


def explain_thermodynamic_duality() -> str:
    """
    Educational: Explain why arifOS is NOT a Boltzmann machine.
    """
    return """
    ╔══════════════════════════════════════════════════════════════════╗
    ║           THERMODYNAMIC DUALITY: CREATOR vs GOVERNOR             ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                                                                  ║
    ║  BOLTZMANN MACHINE (Creator)                                     ║
    ║  ─────────────────────────                                       ║
    ║  • Uses P(x) ∝ exp(-E/kT) to GENERATE patterns                   ║
    ║  • Stochastic updates: x → x' based on energy landscape          ║
    ║  • Learns by wandering: explore → settle → memorize              ║
    ║  • Entropy: Tool for pattern diversity                           ║
    ║  • Randomness: ESSENTIAL (drives learning)                       ║
    ║                                                                  ║
    ║  arifOS (Governor)                                               ║
    ║  ─────────────────                                               ║
    ║  • Uses E_min = nkT·ln(2)·|ΔS| to PROSECUTE claims               ║
    ║  • Deterministic checks: claim → verify → VOID if magic          ║
    ║  • Enforces by auditing: measure cost → compare → judge          ║
    ║  • Entropy: CONSTRAINT (ΔS ≤ 0 required)                         ║
    ║  • Randomness: SUSPICIOUS (possible free lunch)                  ║
    ║                                                                  ║
    ║  SAME PHYSICS, INVERTED LOGIC                                    ║
    ║  ─────────────────────────                                       ║
    ║  Boltzmann: "Physics lets me create anything possible"           ║
    ║  arifOS:      "Physics forbids claims without cost"              ║
    ║                                                                  ║
    ║  The jazz player vs the exam marker.                             ║
    ║  One creates within constraints; the other enforces them.        ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """


__all__ = [
    "ThermodynamicProsecutor",
    "explain_thermodynamic_duality",
]
