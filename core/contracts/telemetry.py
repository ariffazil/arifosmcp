"""
core/contracts/telemetry.py — 3E Intelligence Telemetry Models

Every tool in the 7-tool canonical stack MUST return a ThreeEState.
No tool may emit a bare success without all three phases populated.

3E Mandate (from Grand Unified Technical Specification, FORGED-2026.03):
  E1 Exploration  — hypotheses generated before evidence acquisition
  E2 Entropy      — conflicts, ambiguity, and uncertainty measurement
  E3 Eureka       — final synthesized insight after tri-witness calibration

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# E1: EXPLORATION
# ─────────────────────────────────────────────────────────────────────────────
class ExplorationTelemetry(BaseModel):
    """
    E1: What hypotheses were generated before evidence acquisition?

    Captures the breadth of the search strategy and the sources attempted.
    Must be populated before any evidence retrieval occurs.
    """

    hypotheses: list[str] = Field(
        default_factory=list,
        description="Candidate interpretations or solution paths considered",
    )
    search_strategy: str = Field(
        default="multi_engine",
        description="Strategy used: multi_engine | single_engine | vector_recall | direct_fetch",
    )
    sources_attempted: list[str] = Field(
        default_factory=list,
        description="Engines or endpoints attempted (brave, jina, perplexity, browserless, qdrant)",
    )
    latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Wall-clock time for the exploration phase in milliseconds",
    )
    unknowns: list[str] = Field(
        default_factory=list,
        description="Explicitly acknowledged gaps in knowledge at exploration time",
    )


# ─────────────────────────────────────────────────────────────────────────────
# E2: ENTROPY
# ─────────────────────────────────────────────────────────────────────────────
class EntropyTelemetry(BaseModel):
    """
    E2: What conflicts, ambiguity, and uncertainty were measured?

    F7 Humility (Hard Floor): uncertainty_score MUST be explicitly set.
    No tool may return status=READY without populating this field.
    ΔS (delta_entropy) must be ≤ 0 for a SEAL verdict.
    """

    conflict_count: int = Field(
        default=0,
        ge=0,
        description="Number of contradictions found across evidence sources",
    )
    unstable_assumptions: list[str] = Field(
        default_factory=list,
        description="Claims that rest on weak evidence — MUST be listed for F7 compliance",
    )
    uncertainty_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description=(
            "F7 Humility Band: 0.0=certain, 1.0=total uncertainty. "
            "Forces explicit uncertainty acknowledgment. REQUIRED on every response."
        ),
    )
    source_conflicts: list[str] = Field(
        default_factory=list,
        description="Descriptions of specific source contradictions",
    )
    delta_entropy: float = Field(
        default=0.0,
        description=(
            "ΔS: entropy change from this operation. "
            "Must be ≤ 0 for SEAL (F4 Clarity). Positive value triggers PARTIAL or HOLD."
        ),
    )
    stable_facts: list[str] = Field(
        default_factory=list,
        description="Claims with high confidence and solid evidence backing",
    )


# ─────────────────────────────────────────────────────────────────────────────
# E3: EUREKA
# ─────────────────────────────────────────────────────────────────────────────
class EurekaTelemetry(BaseModel):
    """
    E3: What final insight was synthesized after tri-witness calibration?

    Contains the W3 score, final verdict, and the synthesized insight digest.
    Tri-Witness threshold: W3 ≥ 0.95 required for SEAL.
    """

    insight_digest: str = Field(
        default="",
        description="The synthesized conclusion — human-readable one-liner",
    )
    tri_witness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description=(
            "W3 = (w_H·s_H × w_A·s_A × w_E·s_E)^(1/3). "
            "SEAL threshold: ≥ 0.95. PARTIAL: ≥ 0.75. SABAR: ≥ 0.50."
        ),
    )
    confidence_band: tuple[float, float] = Field(
        default=(0.0, 1.0),
        description="Lower and upper confidence bounds for the insight",
    )
    verdict: str = Field(
        default="SABAR",
        description="SEAL | PARTIAL | SABAR | 888_HOLD | VOID",
    )
    decision_required: list[str] = Field(
        default_factory=list,
        description="Outstanding decisions needed from Sovereign or user before proceeding",
    )


# ─────────────────────────────────────────────────────────────────────────────
# UNIFIED 3E TELEMETRY
# ─────────────────────────────────────────────────────────────────────────────
class ThreeEState(BaseModel):
    """
    3E Intelligence Telemetry — mandatory on every tool output.

    No tool in the 7-tool canonical stack may return a response without
    all three phases populated. This is enforced by the unified_tool_output
    decorator and checked by the kernel's 3E wiring validator.

    Structural anti-hallucination property:
    The system cannot claim SEAL without:
      - eureka.tri_witness_score ≥ 0.95
      - entropy.uncertainty_score explicitly set (not default 0.5)
      - entropy.delta_entropy ≤ 0
    """

    exploration: ExplorationTelemetry = Field(
        default_factory=ExplorationTelemetry,
        description="E1: What hypotheses were considered before evidence acquisition?",
    )
    entropy: EntropyTelemetry = Field(
        default_factory=EntropyTelemetry,
        description="E2: What is uncertain? (F7 Humility mechanized here)",
    )
    eureka: EurekaTelemetry = Field(
        default_factory=EurekaTelemetry,
        description="E3: What insight was forged after tri-witness calibration?",
    )

    def is_seal_eligible(self) -> bool:
        """Hard check: can this 3E state support a SEAL verdict?"""
        return (
            self.eureka.tri_witness_score >= 0.95
            and self.entropy.delta_entropy <= 0.0
            and self.entropy.uncertainty_score < 1.0  # explicitly set, not default
        )

    def to_legacy_intel_state(self) -> dict[str, Any]:
        """Convert to legacy intelligence_state dict for backward compatibility."""
        return {
            "exploration": (
                "EXHAUSTED" if not self.exploration.hypotheses
                else "SCOPED" if len(self.exploration.hypotheses) <= 3
                else "BROAD"
            ),
            "entropy": (
                "CRITICAL" if self.entropy.uncertainty_score > 0.8
                else "HIGH" if self.entropy.uncertainty_score > 0.6
                else "MANAGEABLE" if self.entropy.uncertainty_score > 0.3
                else "LOW"
            ),
            "eureka": (
                "FORGED" if self.eureka.verdict == "SEAL"
                else "PARTIAL" if self.eureka.verdict == "PARTIAL"
                else "NONE"
            ),
            "hypotheses": self.exploration.hypotheses,
            "unknowns": self.exploration.unknowns,
            "stable_facts": self.entropy.stable_facts,
            "unstable_assumptions": self.entropy.unstable_assumptions,
            "conflicts": self.entropy.source_conflicts,
            "uncertainty_score": self.entropy.uncertainty_score,
            "insight": self.eureka.insight_digest or None,
            "confidence": self.eureka.tri_witness_score,
            "decision_required": self.eureka.decision_required,
        }


__all__ = [
    "ExplorationTelemetry",
    "EntropyTelemetry",
    "EurekaTelemetry",
    "ThreeEState",
]
