"""
core/contracts/responses.py — MGI Schema Contracts (Machine → Governance → Intelligence)

The three-layer envelope that enforces strict separation of concerns:
- Layer 1 (Machine): Can it run? (mechanical state)
- Layer 2 (Governance): Should it proceed? (constitutional verdict)
- Layer 3 (Intelligence): How is understanding forged? (3E telemetry)

This schema mechanizes F7 Humility - the LLM cannot return READY without
explicitly calculating uncertainty_score and listing unstable_assumptions.

FORGED-2026.03 additions (Grand Unified Technical Specification):
  MachineEnvelope:    + fault_code, http_diagnostics, tool_name, latency_ms
  GovernanceEnvelope: + hold_id, void_reason, metabolic_stage, floor_scores (dict)
  GovernedResponse:   + three_e (ThreeEState) alias, tri_witness_score shortcut

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# FORGED-2026.03: machine fault codes — NEVER map to VOID
# These are infrastructure signals, not constitutional violations.
MACHINE_FAULT_CODES = frozenset(
    {
        "TOOL_NOT_EXPOSED",  # 404 / endpoint not registered
        "INFRA_DEGRADED",  # service unreachable, 5xx
        "TIMEOUT_EXCEEDED",  # network/compute timeout
        "RATE_LIMITED",  # 429 / quota exceeded
        "DEPENDENCY_UNAVAILABLE",  # Qdrant/Redis/Postgres offline
        "DNS_FAIL",  # DNS resolution failure
        "TLS_FAIL",  # SSL/TLS handshake failure
        "WAF_BLOCK",  # WAF/CDN blocked request
        "PARSE_FAIL",  # Response parse error
        "RENDER_FAIL",  # Headless browser render failure
    }
)


# ---------------------------------------------------------
# LAYER 1: MACHINE (Can it run?)
# ---------------------------------------------------------
class MachineEnvelope(BaseModel):
    """Mechanical layer - system health, session state, continuity."""

    status: Literal["READY", "BLOCKED", "DEGRADED", "FAILED"] = Field(
        default="READY",
        description="Machine operational state",
    )
    issue_label: str | None = Field(
        default=None,
        description="Machine-level issue code (e.g., AUTH_BOOTSTRAP_REQUIRED, TOOL_NOT_EXPOSED)",
    )
    session_id: str = Field(
        default="global",
        description="Active session identifier",
    )
    continuity_state: Literal["UNVERIFIED", "VERIFIED"] = Field(
        default="UNVERIFIED",
        description="F11 continuity state - has valid auth_context been established?",
    )
    # ── FORGED-2026.03 additions ──────────────────────────────────────────────
    tool_name: str = Field(
        default="unknown",
        description="Name of the tool that produced this response",
    )
    latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Wall-clock execution time in milliseconds",
    )
    fault_code: str | None = Field(
        default=None,
        description=(
            "Machine fault code when status=DEGRADED/BLOCKED. "
            "Values from MACHINE_FAULT_CODES set. "
            "CRITICAL: fault_code != VOID — mechanical faults are 888_HOLD, not VOID."
        ),
    )
    http_diagnostics: dict[str, Any] | None = Field(
        default=None,
        description="Forensic HTTP/DNS diagnostics: {status_code, dns_latency_ms, error_count, engines_failed}",
    )


# ---------------------------------------------------------
# LAYER 2: GOVERNANCE (Should it proceed?)
# ---------------------------------------------------------
class GovernanceEnvelope(BaseModel):
    """Constitutional layer - F1-F13 enforcement verdict."""

    verdict: Literal["APPROVED", "PARTIAL", "HOLD", "REJECTED", "VOID"] = Field(
        default="HOLD",
        description="Constitutional verdict from APEX judgment",
    )
    reason: str = Field(
        default="Awaiting constitutional evaluation",
        description="Human-readable explanation of verdict",
    )
    authority_state: Literal["UNVERIFIED", "VERIFIED"] = Field(
        default="UNVERIFIED",
        description="F11 authority state - is actor cryptographically verified?",
    )
    floors_checked: list[str] = Field(
        default_factory=list,
        description="Which constitutional floors were evaluated",
    )
    floors_failed: list[str] = Field(
        default_factory=list,
        description="Which floors blocked execution (if any)",
    )
    # ── FORGED-2026.03 additions ──────────────────────────────────────────────
    floor_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-floor scores: {F1: 1.0, F2: 0.95, ...}. Populated by metabolic loop.",
    )
    hold_id: str | None = Field(
        default=None,
        description="UUID of the 888_HOLD event (populated when verdict=HOLD and reason is sovereign gate)",
    )
    void_reason: str | None = Field(
        default=None,
        description=(
            "Constitutional violation code — populated ONLY on VOID. "
            "Examples: F2_TRUTH_BELOW_THRESHOLD, F11_AUTH_FAILURE, F12_INJECTION, F10_ONTOLOGY. "
            "NEVER populated for mechanical faults (those use machine.fault_code)."
        ),
    )
    metabolic_stage: str = Field(
        default="000",
        description="Current position in the 000→999 metabolic loop when verdict was issued",
    )
    tri_witness_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="W3 score from reality_dossier (if synthesis was performed). ≥ 0.95 required for SEAL.",
    )
    # ── FORGED-2026.03-M27: Apex Governance Ledger ────────────────────────────────
    tokens_consumed: int | None = Field(
        default=None,
        ge=0,
        description="Token budget consumed for this operation (input + output tokens).",
    )
    metabolic_flux: float | None = Field(
        default=None,
        ge=0.0,
        description="Token throughput (tokens/second) at time of decision.",
    )
    latency_jitter_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Latency variance from baseline (absolute deviation in ms).",
    )
    grounding_quality: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Evidence grounding quality (0=no grounding, 1=fully grounded via external verification).",
    )
    source_freshness_hours: float | None = Field(
        default=None,
        ge=0.0,
        description="Age of newest source in hours (if applicable). None means no external source.",
    )
    blast_radius_estimate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Estimated blast radius if safety check is skipped (0=contained, 1=catastrophic).",
    )
    recovery_time_estimate: str | None = Field(
        default=None,
        description="Human-readable estimated recovery time if this action fails (e.g., '2 hours', 'permanent').",
    )


# ---------------------------------------------------------
# LAYER 3: INTELLIGENCE / 3E (How is understanding forged?)
# ---------------------------------------------------------
class ExplorationState(BaseModel):
    """E1: Exploration phase - gathering candidate interpretations."""

    phase: Literal["BROAD", "SCOPED", "EXHAUSTED"] = Field(
        default="BROAD",
        description="How thoroughly has the hypothesis space been explored?",
    )
    hypotheses: list[str] = Field(
        default_factory=list,
        description="Candidate interpretations or solution paths considered",
    )
    unknowns: list[str] = Field(
        default_factory=list,
        description="Explicitly acknowledged gaps in knowledge",
    )


class EntropyState(BaseModel):
    """E2: Entropy phase - measuring and metabolizing uncertainty."""

    phase: Literal["LOW", "MANAGEABLE", "HIGH", "CRITICAL"] = Field(
        default="MANAGEABLE",
        description="Current entropy/uncertainty level",
    )
    stable_facts: list[str] = Field(
        default_factory=list,
        description="Claims with high confidence and solid evidence",
    )
    unstable_assumptions: list[str] = Field(
        default_factory=list,
        description="Claims that rest on shaky ground - MUST be listed for F7 compliance",
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="Contradictions or tensions in the evidence",
    )
    uncertainty_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="F7 Humility Band: 0=certain, 1=total uncertainty. Forces explicit uncertainty acknowledgment.",
    )


class EurekaState(BaseModel):
    """E3: Eureka phase - collapsing confusion into coherent insight."""

    phase: Literal["NONE", "PARTIAL", "FORGED"] = Field(
        default="NONE",
        description="Has a coherent insight been synthesized?",
    )
    insight: str | None = Field(
        default=None,
        description="The synthesized conclusion or proposal",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the insight (0-1 scale)",
    )
    decision_required: list[str] = Field(
        default_factory=list,
        description="Outstanding decisions needed from Sovereign or user",
    )


class IntelligenceEnvelope(BaseModel):
    """The 3E cycle: Exploration → Entropy → Eureka."""

    exploration: ExplorationState = Field(
        default_factory=ExplorationState,
        description="E1: What hypotheses were considered?",
    )
    entropy: EntropyState = Field(
        default_factory=EntropyState,
        description="E2: What is uncertain? (F7 Humility mechanized here)",
    )
    eureka: EurekaState = Field(
        default_factory=EurekaState,
        description="E3: What insight was forged?",
    )


# ---------------------------------------------------------
# THE UNIFIED CANONICAL RESPONSE
# ---------------------------------------------------------
class GovernedResponse(BaseModel):
    """
    The complete MGI envelope - every governed tool returns this.

    This schema structurally forces the AI to:
    1. Declare mechanical state (Machine)
    2. Submit to constitutional judgment (Governance)
    3. Metabolize uncertainty before answering (Intelligence/3E)

    Anti-hallucination property: The model cannot return status=READY
    without filling out entropy.unstable_assumptions and uncertainty_score.
    """

    machine: MachineEnvelope = Field(
        default_factory=MachineEnvelope,
        description="Layer 1: Mechanical state (can it run?)",
    )
    governance: GovernanceEnvelope = Field(
        default_factory=GovernanceEnvelope,
        description="Layer 2: Constitutional verdict (should it proceed?)",
    )
    intelligence: IntelligenceEnvelope = Field(
        default_factory=IntelligenceEnvelope,
        description="Layer 3: 3E telemetry (how was understanding forged?)",
    )

    # Extension slot for tool-specific payload
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific result data",
    )

    # Audit trail
    provenance: dict[str, Any] = Field(
        default_factory=dict,
        description="Chain of custody for this response",
    )


# ---------------------------------------------------------
# CONVERSION HELPERS (MGI ↔ RuntimeEnvelope)
# ---------------------------------------------------------
def runtime_envelope_to_governed(runtime_env: dict[str, Any]) -> GovernedResponse:
    """Convert legacy RuntimeEnvelope to strict MGI GovernedResponse."""

    # Extract machine state
    machine = MachineEnvelope(
        status="READY" if runtime_env.get("ok") else "BLOCKED",
        issue_label=runtime_env.get("machine_issue"),
        session_id=runtime_env.get("session_id", "global"),
        continuity_state="VERIFIED" if runtime_env.get("auth_context") else "UNVERIFIED",
    )

    # Extract governance state
    verdict_map = {
        "SEAL": "APPROVED",
        "PARTIAL": "PARTIAL",
        "HOLD": "HOLD",
        "HOLD_888": "HOLD",
        "VOID": "REJECTED",
        "SABAR": "HOLD",
    }
    raw_verdict = runtime_env.get("verdict", "HOLD")
    governance = GovernanceEnvelope(
        verdict=verdict_map.get(raw_verdict, "HOLD"),
        reason=runtime_env.get("status", "Unknown"),
        authority_state="VERIFIED" if runtime_env.get("auth_context") else "UNVERIFIED",
    )

    # Extract intelligence state (if present)
    intel_data = runtime_env.get("intelligence_state", {})
    intelligence = IntelligenceEnvelope(
        exploration=ExplorationState(
            phase=intel_data.get("exploration", "BROAD"),
            hypotheses=intel_data.get("hypotheses", []),
            unknowns=intel_data.get("unknowns", []),
        ),
        entropy=EntropyState(
            phase=intel_data.get("entropy", "MANAGEABLE"),
            stable_facts=intel_data.get("stable_facts", []),
            unstable_assumptions=intel_data.get("unstable_assumptions", []),
            conflicts=intel_data.get("conflicts", []),
            uncertainty_score=intel_data.get("uncertainty_score", 0.5),
        ),
        eureka=EurekaState(
            phase=intel_data.get("eureka", "NONE"),
            insight=intel_data.get("insight"),
            confidence=intel_data.get("confidence", 0.0),
            decision_required=intel_data.get("decision_required", []),
        ),
    )

    return GovernedResponse(
        machine=machine,
        governance=governance,
        intelligence=intelligence,
        payload=runtime_env.get("payload", {}),
        provenance={"source": "runtime_envelope_conversion"},
    )


def governed_to_runtime_envelope(governed: GovernedResponse) -> dict[str, Any]:
    """Convert strict MGI GovernedResponse to legacy RuntimeEnvelope format."""

    verdict_map = {
        "APPROVED": "SEAL",
        "PARTIAL": "PARTIAL",
        "HOLD": "HOLD",
        "REJECTED": "VOID",
    }

    return {
        "ok": governed.machine.status == "READY",
        "tool": governed.payload.get("tool", "unknown"),
        "session_id": governed.machine.session_id,
        "stage": governed.payload.get("stage", "000_INIT"),
        "verdict": verdict_map.get(governed.governance.verdict, "HOLD"),
        "status": "SUCCESS" if governed.machine.status == "READY" else "ERROR",
        "machine_status": governed.machine.status,
        "machine_issue": governed.machine.issue_label,
        "intelligence_state": {
            "exploration": governed.intelligence.exploration.phase,
            "entropy": governed.intelligence.entropy.phase,
            "eureka": governed.intelligence.eureka.phase,
            "hypotheses": governed.intelligence.exploration.hypotheses,
            "unknowns": governed.intelligence.exploration.unknowns,
            "stable_facts": governed.intelligence.entropy.stable_facts,
            "unstable_assumptions": governed.intelligence.entropy.unstable_assumptions,
            "conflicts": governed.intelligence.entropy.conflicts,
            "uncertainty_score": governed.intelligence.entropy.uncertainty_score,
            "insight": governed.intelligence.eureka.insight,
            "confidence": governed.intelligence.eureka.confidence,
            "decision_required": governed.intelligence.eureka.decision_required,
        },
        "payload": governed.payload,
    }


__all__ = [
    "MACHINE_FAULT_CODES",
    "MachineEnvelope",
    "GovernanceEnvelope",
    "IntelligenceEnvelope",
    "ExplorationState",
    "EntropyState",
    "EurekaState",
    "GovernedResponse",
    "runtime_envelope_to_governed",
    "governed_to_runtime_envelope",
]
