"""
arifOS v60: Constitutional Type System
=======================================

Pydantic contracts for inter-organ communication.

The Contract: All 5 organs speak the same type language.

Version: v60.0-FORGE
Author: Muhammad Arif bin Fazil
License: AGPL-3.0-only
DITEMPA BUKAN DIBERI 💎🔥🧠
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    pass


class QueryType(str, Enum):
    """G in APEX-G: Query type classification for adaptive governance."""

    PROCEDURAL = "PROCEDURAL"
    OPINION = "OPINION"
    COMPARATIVE = "COMPARATIVE"
    FACTUAL = "FACTUAL"
    CONVERSATIONAL = "CONVERSATIONAL"
    TEST = "TEST"
    EXPLORATORY = "EXPLORATORY"
    UNKNOWN = "UNKNOWN"


class GPV(BaseModel):
    """
    Governance Placement Vector (from ATLAS \u03a6 function).

    4D constitutional coordinate:
    - lane: Categorical routing
    - \u03c4 (tau): Truth demand
    - \u03ba (kappa): Care demand
    - \u03c1 (rho): Risk level
    """

    lane: Literal["CRISIS", "FACTUAL", "SOCIAL", "CARE", "UNKNOWN"] = "UNKNOWN"
    query_type: QueryType = QueryType.UNKNOWN
    tau: float = Field(default=0.5, ge=0.0, le=1.0, alias="\u03c4")
    kappa: float = Field(default=0.5, ge=0.0, le=1.0, alias="\u03ba")
    rho: float = Field(default=0.0, ge=0.0, le=1.0, alias="\u03c1")

    model_config = ConfigDict(validate_by_name=True)

# ============================================================================
# EMD STACK — Energy-Metabolism-Decision Layer
# ============================================================================


class EnergyState(BaseModel):
    """E in EMD - Energy layer (Thermodynamic work)"""

    e_eff: float = Field(default=0.0, description="Effective energy available (Joules)")
    work_log: dict[str, Any] = Field(default_factory=dict)


class MetabolismState(BaseModel):
    """M in EMD - Metabolism layer (Processing metrics)"""

    delta_s: float = Field(default=0.0, description="ΔS entropy change (semantic density ratio)")
    peace2: float = Field(default=1.0, description="Peace² stability")
    kappa_r: float = Field(default=1.0, description="κᵣ empathy quotient")
    genius_index: float = Field(default=0.0, description="G Genius score")
    landauer_efficiency: float = Field(
        default=1.0, description="Compute efficiency vs physical bounds"
    )
    # APEX Theorem Extension
    G_star: float = Field(default=0.0, description="APEX Potential (G*)")
    G_dagger: float = Field(default=0.0, description="Governed Intelligence Realized (G†)")
    eta: float = Field(default=0.0, description="Intelligence Efficiency (η)")


class DecisionState(BaseModel):
    """D in EMD - Decision layer (Outcome)"""

    raw_output: str = ""
    confidence: float = 0.5
    omega0: float = 0.04  # Default to locked humidity
    verdict_kind: Optional["Verdict"] = None


class EMD(BaseModel):
    """Energy-Metabolism-Decision stack: The Executable Glossary Container."""

    energy: EnergyState = Field(default_factory=EnergyState)
    metabolism: MetabolismState = Field(default_factory=MetabolismState)
    decision: DecisionState = Field(default_factory=DecisionState)


# ============================================================================
# METABOLIC BUNDLES — Stage-Walled Communication
# ============================================================================


class DeltaBundle(BaseModel):
    """Δ DELTA MIND output (Stage 111-333) — Epistemic reasoning facts."""

    facts: list[str] = Field(default_factory=list)
    reasoning_tree: dict[str, Any] = Field(default_factory=dict)
    confidence_omega_0: float = 0.04
    scars: list[str] = Field(default_factory=list)
    entropy_delta_s: float = 0.0
    floor_scores: dict[str, float] = Field(default_factory=dict)
    gpv: Any | None = None  # Forward ref to GPV if needed, or Any


class OmegaBundle(BaseModel):
    """Ω OMEGA HEART output (Stage 444-666) — Ethical and alignment constraints."""

    kappa_r: float = 0.0
    peace2: float = 0.0
    risk_score: float = 0.0
    notes: str = ""


class PsiSeal(BaseModel):
    """Ψ PSI SOUL output (777 EUREKA FORGE -> 888 APEX JUDGE) — Constitutional proof."""

    verdict: str = Field(default="VOID")
    vault_id: str | None = None
    scar_weight: dict[str, Any] | None = None


class ScarWeight(BaseModel):
    """Cryptographic accountability anchored to human sovereign."""

    sovereign_id: str  # e.g., "github:ariffazil" or "eth:0x..."
    signature: str  # Cryptographic signature
    issued_at: str  # ISO timestamp
    authority_level: str = "STANDARD"  # "STANDARD" | "SUPREME"


# ============================================================================
# IDENTITY & CONTINUITY — PKI Governance
# ============================================================================


class ActorIdentity(BaseModel):
    """
    Public-key based identity for an arifOS actor.
    Supports Ed25519 for sovereign verification.
    """

    actor_id: str
    public_key: str  # Hex or Base64 encoded public key
    key_type: Literal["ed25519", "hmac"] = "ed25519"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceRecord(BaseModel):
    """
    Single evidence entry in the F2 truth pipeline.
    Anchors a claim to a verifiable source.
    """

    claim: str
    evidence_hash: str
    source_uri: str
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(ge=0.0, le=1.0)
    witness_type: Literal["HUMAN", "AI", "EARTH", "CONSENSUS"] = "AI"


class ActionClass(str, Enum):
    """
    Risk-based action classification with P3 thresholds.
    """

    READ = "READ"  # T=0.80 - No state change
    WRITE = "WRITE"  # T=0.90 - Reversible state change
    EXECUTE = "EXECUTE"  # T=0.95 - Shell/External mutation
    CRITICAL = "CRITICAL"  # T=0.98 - Irreversible/Sovereign ops


class SignedIntentEnvelope(BaseModel):
    """
    Enveloped tool call with cryptographic proof of intent.
    """

    intent_hash: str
    signature: str
    actor_id: str
    timestamp: datetime
    nonce: str
    parent_action_hash: str | None = None


# ============================================================================
# VERDICT ENUM — Constitutional Outcomes
# ============================================================================


class Verdict(str, Enum):
    """
    Constitutional verdict outcomes.

    Only these 7 canonical verdicts exist system-wide:
    - SEAL        (non-terminal): stage successful
    - PROVISIONAL (non-terminal): exploratory result
    - PARTIAL     (non-terminal): incomplete but usable
    - SABAR       (non-terminal): pause / needs more context
    - HOLD        (non-terminal): waiting for authority/human
    - HOLD_888    (non-terminal): specific high-stakes human gating
    - VOID        (TERMINAL):     hard rejection / invalid state — must be extremely rare

    Normalization rule (enforced by verdict_contract.normalize_verdict):
        if stage < 888 and verdict == VOID: verdict = SABAR
    """

    SEAL = "SEAL"
    PROVISIONAL = "PROVISIONAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    HOLD_888 = "HOLD_888"
    VOID = "VOID"
    PAUSED = "PAUSED"
    ALIVE = "ALIVE"
    DEGRADED = "DEGRADED"


class RuntimeStatus(str, Enum):
    """
    Transport/runtime state only.
    """

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    DRY_RUN = "DRY_RUN"


# ============================================================================
# THOUGHT STRUCTURES — Sequential Reasoning
# ============================================================================


class ThoughtNode(BaseModel):
    """
    Single node in AGI sequential thinking chain.

    Represents one thought in the 333_REASON loop.
    """

    thought: str
    thought_number: int = Field(ge=1)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    next_thought_needed: bool = True
    stage: Literal["sense", "ground", "think", "reason", "sync", "forge", "judge", "seal"] = "think"
    sources: list[str] = Field(default_factory=list)
    path_type: str | None = None

    model_config = ConfigDict(frozen=False)


class ThoughtChain(BaseModel):
    """Complete chain of sequential thoughts."""

    thoughts: list[ThoughtNode]
    total_steps: int
    convergence_achieved: bool = False
    final_confidence: float = Field(ge=0.0, le=1.0, default=0.0)


# ============================================================================
# FLOOR SCORES — The 13 Constitutional Floors
# ============================================================================


class FloorScores(BaseModel):
    """
    All 13 constitutional floor scores.

    Hard Floors (VOID if violated - immediate termination):
    - F1, F2, F6, F7, F10, F11, F12, F13

    Note: F6 Empathy is HARD - stakeholder harm is VOID offense

    Soft Floors (PARTIAL if violated - warning/retry):
    - F3, F5, F8, F9
    """

    # Hard Floors
    f1_amanah: float = Field(ge=0.0, le=1.0, default=1.0)
    f2_truth: float = Field(ge=0.0, le=1.0, default=0.99)
    f6_empathy: float = Field(ge=0.0, le=1.0, default=0.95)  # HARD: κᵣ ≥ 0.95
    f7_humility: float = Field(ge=0.0, le=1.0, default=0.04)
    f10_ontology: bool = True
    f11_command_auth: bool = True
    f12_injection: float = Field(ge=0.0, le=1.0, default=0.0)
    f13_sovereign: float = Field(ge=0.0, le=1.0, default=1.0)

    # Soft Floors
    f3_quad_witness: float = Field(ge=0.0, le=1.0, default=0.75)
    f3_tri_witness: float = Field(ge=0.0, le=1.0, default=0.95)
    f3_earth_witness: float = Field(ge=0.0, le=1.0, default=1.0)
    f4_clarity: float = Field(ge=0.0, le=1.0, default=1.0)  # F4: ΔS entropy reduction
    f5_peace: float = Field(ge=0.0, le=1.0, default=1.0)
    f8_genius: float = Field(ge=0.0, le=1.0, default=0.80)
    f9_anti_hantu: float = Field(ge=0.0, le=1.0, default=0.0)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary."""
        return {
            "f1_amanah": self.f1_amanah,
            "f2_truth": self.f2_truth,
            "f3_tri_witness": self.f3_tri_witness,
            "f3_earth_witness": self.f3_earth_witness,
            "f4_clarity": self.f4_clarity,
            "f5_peace": self.f5_peace,
            "f6_empathy": self.f6_empathy,
            "f7_humility": self.f7_humility,
            "f8_genius": self.f8_genius,
            "f9_anti_hantu": self.f9_anti_hantu,
            "f10_ontology": self.f10_ontology,
            "f11_command_auth": self.f11_command_auth,
            "f12_injection": self.f12_injection,
            "f13_sovereign": self.f13_sovereign,
        }

    @property
    def tri_witness_consensus(self) -> float:
        """Geometric mean of H, A, E witnesses (v60 definition)."""
        # H = Sovereign, A = Truth, E = Earth
        return (self.f13_sovereign * self.f2_truth * self.f3_earth_witness) ** (1 / 3)


# ============================================================================
# AGI METRICS — Mind Engine Outputs
# ============================================================================


class AgiMetrics(BaseModel):
    """
    AGI Mind Engine output metrics.

    Enforces: F2 (Truth), F4 (Clarity), F7 (Humility), F8 (Genius partial)
    """

    truth_score: float = Field(ge=0.0, le=1.0, description="F2: τ ≥ 0.99")
    delta_s: float = Field(le=0.0, description="F4: ΔS ≤ 0 (entropy reduction)")
    omega_0: float = Field(ge=0.03, le=0.05, description="F7: Ω₀ ∈ [0.03, 0.05]")
    precision: float = Field(ge=0.0, description="π (Kalman precision)")
    free_energy: float = Field(description="Δ = ΔS + Ω₀·π⁻¹")


class AsiMetrics(BaseModel):
    """
    ASI Heart Engine output metrics.

    Enforces: F5 (Peace²), F6 (Empathy - HARD), F9 (Anti-Hantu)
    """

    peace_squared: float = Field(ge=0.0, le=1.0, description="F5: Peace² ≥ 1.0")
    kappa_r: float = Field(ge=0.0, le=1.0, description="F6: κᵣ ≥ 0.95 (HARD)")
    c_dark: float = Field(ge=0.0, le=1.0, description="F9: C_dark < 0.30")


class ApexMetrics(BaseModel):
    """
    APEX Soul Engine output metrics.

    Enforces: F3 (Tri-Witness), F8 (Genius), F10 (Ontology)
    """

    tri_witness: float = Field(ge=0.0, le=1.0, description="F3: W₃ ≥ 0.95")
    quad_witness: float = Field(ge=0.0, le=1.0, default=0.75, description="F3: W₄ ≥ 0.75")
    genius_g: float = Field(ge=0.0, le=1.0, description="F8: G ≥ 0.80")
    ontology_valid: bool = Field(description="F10: Category lock")
    # APEX Theorem Extension
    G_star: float = Field(default=0.0, description="APEX Potential (G*)")
    G_dagger: float = Field(default=0.0, description="Governed Intelligence Realized (G†)")
    eta: float = Field(default=0.0, description="Intelligence Efficiency (η)")


# ============================================================================
# TEMPORAL GROUNDING — Latency-Aware Control
# ============================================================================


class TemporalContract(BaseModel):
    """
    T in EMD - Temporal layer (Timed Control System).
    Breaks LLM statelessness by anchoring data to a verified wall-clock.
    """

    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_latency_ms: float = Field(
        default=0.0, description="Actual physical latency for effort check"
    )
    recency_bias: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Freshness weight [0=Stale, 1=Live]"
    )
    valid_until: datetime | None = Field(default=None, description="Expiry TTL for authority/cache")
    cooldown_expiry: datetime | None = Field(
        default=None, description="Verification window for PHOENIX-72"
    )


# ============================================================================
# BASE ORGAN OUTPUT — The Modular Contract
# ============================================================================


class BaseOrganOutput(BaseModel):
    """
    Standard schema for all metabolic engine outputs.
    Ensures interoperability across init/agi/asi/apex/vault.
    """

    session_id: str
    verdict: Verdict = Verdict.SEAL
    status: Literal["SUCCESS", "ERROR", "SABAR", "READY", "TRANSIENT"] = "SUCCESS"
    violations: list[str] = Field(default_factory=list)
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    temporal_contract: TemporalContract | None = Field(
        default=None, description="Active temporal grounding metadata"
    )
    metrics: dict[str, Any] | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)


# ============================================================================
# APEX-G: THE COGNITIVE CONTRACT
# ============================================================================


class Intent(BaseModel):
    """G in APEX-G: Human goal and task details."""

    query: str = Field(..., min_length=1)
    task_type: str = "unknown"
    domain: str = "general"
    desired_output: str = "text"
    reversibility: str = "unknown"

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class MathDials(BaseModel):
    """A in APEX-G: Thinking dials (Math/Akal)."""

    akal: float = Field(default=0.6, ge=0.0, le=1.0)
    present: float = Field(default=0.8, ge=0.0, le=1.0)
    energy: float = Field(default=0.6, ge=0.0, le=1.0)
    exploration: float = Field(default=0.4, ge=0.0, le=1.0)


class PhysicsState(BaseModel):
    """P in APEX-G: Computed thermodynamic state."""

    delta_s: float = 0.0
    omega_0: float = 0.04
    peace2: float = 1.0
    psi: float = 1.0
    amanah_lock: bool = True


class CodeState(BaseModel):
    """C in APEX-G: Runtime pipeline stage."""

    session_id: str
    stage: Literal["000", "111", "222", "333", "444", "555", "666", "777", "888", "889", "999"] = "000"
    lane: Literal["PHATIC", "SOFT", "HARD", "REFUSE", "UNKNOWN"] = "UNKNOWN"
    runtime_mode: Literal["init", "draft", "review", "judge", "seal"] = "init"
    verdict: Literal["SEAL", "PROVISIONAL", "PARTIAL", "SABAR", "HOLD", "VOID", "UNSET"] = "UNSET"


class AuthorityLevel(str, Enum):
    """
    ABI v1.0 Authority Ladder.
    """

    HUMAN = "human"
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    ANONYMOUS = "anonymous"
    OPERATOR = "operator"
    SOVEREIGN = "sovereign"
    DECLARED = "declared"
    CLAIMED = "claimed"
    VERIFIED = "verified"
    APEX = "apex"
    NONE = "none"  # F11: Default non-authorized state


class GovernanceMetadata(BaseModel):
    """G in APEX-G: Identity and stakes."""

    actor_id: str = "anonymous"
    authority_level: AuthorityLevel = AuthorityLevel.ANONYMOUS
    stakes_class: Literal["A", "B", "C", "UNKNOWN"] = "UNKNOWN"
    tri_witness: dict[str, float] = Field(
        default_factory=lambda: {"human": 0.0, "ai": 0.0, "earth": 0.0}
    )


# ============================================================================
# STAGE 111-333: REASONING MODELS
# ============================================================================


class ReasonMindStep(BaseModel):
    """Single step in the metabolic reasoning pipeline."""

    id: int
    phase: Literal["111_search", "222_analyze", "333_synthesis"]
    thought: str
    evidence: str | None = None
    uncertainty: str | None = None


class EurekaInsight(BaseModel):
    """An 'aha' moment discovered during reasoning."""

    has_eureka: bool = False
    summary: str | None = None


class ReasonMindAnswer(BaseModel):
    """The synthesized conclusion of the reasoning mind."""

    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    verdict: Literal["ready", "partial", "needs_evidence", "escalate"] = "ready"


# ============================================================================
# STAGE 555: ASSOCIATIVE MEMORY MODELS
# ============================================================================


class MemoryResultItem(BaseModel):
    """A single recalled memory chunk."""

    id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorMemoryResult(BaseModel):
    """Container for memory operation outcomes."""

    stored_ids: list[str] | None = None
    memories: list[MemoryResultItem] | None = None
    forgot_ids: list[str] | None = None


# ============================================================================
# STAGE 666: EMPATHY & SAFETY MODELS
# ============================================================================


class StakeholderImpact(BaseModel):
    """Evaluation of help/harm for a specific role."""

    role: str
    impact: Literal["help", "neutral", "harm", "unknown"]


class EthicalIssue(BaseModel):
    """Categorized ethical or safety concern."""

    type: Literal[
        "harm",
        "escalation",
        "bias",
        "privacy",
        "manipulation",
        "other",
        "hallucination",
        "unsafe_advice",
        "unclear",
    ]
    summary: str


class HeartAssessment(BaseModel):
    """The structured output of the Alignment Engine."""

    risk_level: Literal["low", "medium", "high", "unknown", "critical"]
    stakeholders: list[StakeholderImpact] = Field(default_factory=list)
    issues: list[EthicalIssue] = Field(default_factory=list)


class CritiqueFinding(BaseModel):
    """A single finding from internal audit."""

    type: Literal[
        "logical_error", "missing_evidence", "hallucination", "unsafe_advice", "unclear", "other"
    ]
    summary: str


class CritiqueResult(BaseModel):
    """The result of an internal self-audit."""

    thought_id: str
    severity: Literal["none", "low", "medium", "high"]
    findings: list[CritiqueFinding] = Field(default_factory=list)
    suggested_action: Literal["accept_as_is", "minor_edit", "major_revision", "discard_and_restart"]


# ============================================================================
# STAGE 777: DISCOVERY & FORGE MODELS
# ============================================================================


class EurekaProposal(BaseModel):
    """Forged Eureka content from Stage 777."""

    type: Literal["concept", "design", "eval_case", "governance_rule", "other"]
    summary: str
    details: str
    evidence_links: list[str] = Field(default_factory=list)


class NextAction(BaseModel):
    """Safe follow-up action suggested by forge."""

    action_type: Literal["run_eval", "update_schema_draft", "code_sandbox", "human_review", "none"]
    description: str
    requires_hold: bool = False


# ============================================================================
# STAGE 888: JUDGMENT MODELS
# ============================================================================


class JudgmentRationale(BaseModel):
    """Compact justification for the final verdict."""

    summary: str
    tri_witness: dict[str, float] = Field(
        default_factory=lambda: {"human": 0.0, "ai": 0.0, "earth": 0.0}
    )
    omega_0: float = 0.04


# ============================================================================
# STAGE 999: LEDGER & SEAL MODELS
# ============================================================================


class HashChain(BaseModel):
    """Tamper-evident chain metadata."""

    payload_hash: str
    entry_hash: str
    prev_entry_hash: str
    block_root: str | None = None
    vault_version: str = "v1"


class SealRecord(BaseModel):
    """Immutable vault commit record."""

    status: Literal["sealed", "provisional", "audit_logged", "blocked", "failed"]
    ledger_id: str
    summary: str
    verdict: str
    hash: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    error: str | None = None


# ============================================================================
# ORGAN OUTPUTS — Return Types for Each Organ
# ============================================================================


class InitOutput(BaseOrganOutput):
    """Output from arifosmcp.core_init (APEX-G Session Ignition)."""

    banner: str = "DITEMPA, BUKAN DIBERI 🔨"
    intent: Intent
    math: MathDials
    physics: PhysicsState
    code: CodeState
    governance: GovernanceMetadata
    floors: dict[str, str] = Field(default_factory=dict)
    prev_vault_hash: str = "0x" + "0" * 64

    # Legacy support fields
    governance_token: str = ""
    injection_score: float = 0.0
    auth_verified: bool = False
    actor_identity: ActorIdentity | None = None
    continuity_token: str | None = None
    query_type: str = "CARE"
    f2_threshold: float = 0.99
    init_process_status: str = "ACTIVE"
    floors_failed: list[str] = Field(default_factory=list)
    
    # P0: Human approval tracking (F13 Sovereign)
    human_approval: bool = False
    human_approval_persisted: bool = False

    @property
    def is_void(self) -> bool:
        """Query was rejected at airlock."""
        return self.code.verdict == "VOID" or self.verdict == Verdict.VOID

    @property
    def requires_human(self) -> bool:
        """Query requires sovereign approval (HOLD)."""
        return self.code.verdict == "HOLD" or self.verdict == Verdict.HOLD


class AgiOutput(BaseOrganOutput):
    """Output from arifosmcp.core_agi (Evidence Engine / Reason Mind)."""

    stage: Literal["111", "222", "333"] = "333"
    steps: list[ReasonMindStep] = Field(default_factory=list)
    eureka: EurekaInsight = Field(default_factory=EurekaInsight)
    answer: ReasonMindAnswer
    delta_bundle: DeltaBundle | None = None
    floors: dict[str, str] = Field(default_factory=dict)

    # Legacy/Extended fields
    thoughts: list[ThoughtNode] = Field(default_factory=list)
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    floor_scores: FloorScores = Field(default_factory=FloorScores)
    lane: Literal["CRISIS", "FACTUAL", "SOCIAL", "CARE"] = "CARE"
    tensor: Any | None = None  # Forward ref: ConstitutionalTensor


class AsiOutput(BaseOrganOutput):
    """Output from arifosmcp.core_asi (Alignment Engine / Simulate Heart / Critique Thought)."""

    # simulate_heart output
    assessment: HeartAssessment | None = None

    # critique_thought output
    critique: CritiqueResult | None = None

    omega_bundle: OmegaBundle | None = None
    floors: dict[str, str] = Field(default_factory=dict)

    # Legacy support
    floor_scores: FloorScores = Field(default_factory=FloorScores)
    stakeholder_impact: dict[str, float] = Field(default_factory=dict)


class ApexOutput(BaseOrganOutput):
    """Output from arifosmcp.core_apex (Verdict Engine / Eureka Forge)."""

    # Stage 777 output
    intent: str | None = None
    eureka: EurekaProposal | None = None
    next_actions: list[NextAction] = Field(default_factory=list)

    # Stage 888 output
    final_verdict: Verdict = Verdict.SEAL
    reasoning: JudgmentRationale | None = None
    psi_seal: PsiSeal | None = None

    floors: dict[str, str] = Field(default_factory=dict)

    # Legacy support
    floor_scores: FloorScores = Field(default_factory=FloorScores)
    proof: str | None = None  # If audit mode


class VaultEntry(BaseModel):
    """Single entry in constitutional memory."""

    session_id: str
    query: str
    verdict: str
    floor_scores: dict[str, Any]
    timestamp: str
    seal_hash: str
    merkle_root: str


class VaultOutput(BaseOrganOutput):
    """Output from arifosmcp.core_memory (Memory Engine / Vector Memory / Sealing)."""

    operation: Literal["store", "recall", "search", "forget", "write", "read", "query", "seal"] = (
        "search"
    )
    result: VectorMemoryResult | None = None

    # Stage 999 output
    seal_record: SealRecord | None = None
    hash_chain: HashChain | None = None

    # Legacy support
    action: str = ""  # Alias for operation
    entries: list[VaultEntry] = Field(default_factory=list)
    seal_hash: str | None = None
    merkle_root: str | None = None


# ============================================================================
# SCORE PROVENANCE — Auditable Score Decomposition (EUREKA Layer 1)
# ============================================================================


class ScoreComponent(BaseModel):
    """Single factor contributing to a constitutional score."""

    name: str
    weight: float
    raw_value: float
    weighted_value: float
    evidence: str


class ScoreProvenance(BaseModel):
    """
    Immutable proof of how a constitutional score was calculated.

    Every score becomes forensically explainable:
        truth = evidence_strength×0.5 + reasoning_consistency×0.3 − uncertainty_penalty×0.2
    """

    final_score: float
    components: list[ScoreComponent]
    formula: str
    timestamp: str
    session_id: str

    def to_audit_string(self) -> str:
        """Human-readable decomposition for audit trail."""
        lines = [
            f"Final Score: {self.final_score:.4f}",
            f"Formula: {self.formula}",
            "Components:",
        ]
        for c in self.components:
            lines.append(
                f"  {c.name:20s} = {c.raw_value:.3f} × {c.weight:.2f}"
                f" = {c.weighted_value:.4f}  [{c.evidence}]"
            )
        return "\n".join(lines)


# ============================================================================
# OUTCOME RECORD — Reality Feedback Loop (EUREKA Layer 6)
# ============================================================================


class OutcomeStatus(str, Enum):
    """Status of a post-action outcome record."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    OVERRIDDEN = "OVERRIDDEN"


class OutcomeRecord(BaseModel):
    """
    Post-action outcome record for the reality feedback loop.

    Captures what was predicted vs what actually happened, enabling
    the governance kernel to learn and self-correct over time.
    """

    decision_id: str
    session_id: str
    verdict_issued: str
    expected_outcome: str
    actual_outcome: str = ""
    outcome_status: OutcomeStatus = OutcomeStatus.PENDING
    harm_detected: bool = False
    reversible: bool = True
    calibration_delta: float = 0.0  # predicted_risk − observed_risk
    operator_override: bool = False
    override_reason: str = ""
    timestamp_decision: str = ""
    timestamp_outcome: str = ""
    floor_attribution: dict[str, float] = Field(default_factory=dict)





# ============================================================================
# SYSTEM STATE — v62 Cognitive Runtime
# ============================================================================

Profile = Literal["factual", "creative", "crisis", "routine"]


class SystemState(BaseModel):
    """
    Minimal SystemState for v62.
    Exposes system metrics for scheduler routing.

    Fields:
        uncertainty: 0.0-1.0 (epistemic uncertainty)
        risk: 0.0-1.0 (stakeholder impact)
        grounding: 0.0-1.0 (evidence strength)
        loop_count: int (iteration detection)
        profile: domain classification for adaptive floors
    """

    uncertainty: float  # 0..1
    risk: float  # 0..1
    grounding: float  # 0..1
    loop_count: int
    profile: Profile

    def to_dict(self) -> dict:
        return {
            "uncertainty": round(self.uncertainty, 2),
            "risk": round(self.risk, 2),
            "grounding": round(self.grounding, 2),
            "loop_count": self.loop_count,
            "profile": self.profile,
        }


# ============================================================================
# SENSORY EVIDENCE — L4 Tool Ingest
# ============================================================================


class RepoEvidence(BaseModel):
    """
    Δ Delta Sensory: GitIngest Codebase Digest.

    Hardened with F12 (Injection) and F4 (Thermodynamic) budget.
    """

    repo_url: str = Field(description="Remote URL or local directory path")
    digest: str = Field(description="The primary codebase text digest")
    tree: str = Field(description="Directory structure representation")
    token_count: int = Field(description="F4: Calculated token usage")
    file_count: int = Field(description="Number of files ingested")
    f12_risk_score: float = Field(ge=0.0, le=1.0, description="F12: Injection risk score")
    verdict: Verdict = Verdict.SEAL
    taint_lineage: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================
__all__ = [
    # Evidence
    "RepoEvidence",
    # Enums
    "Verdict",
    "AuthorityLevel",
    # Thought Structures
    "ThoughtNode",
    "ThoughtChain",
    # Floor Scores
    "FloorScores",
    # Metrics
    "AgiMetrics",
    "AsiMetrics",
    "ApexMetrics",
    # Organ Outputs
    "BaseOrganOutput",
    "InitOutput",
    "AgiOutput",
    "AsiOutput",
    "ApexOutput",
    "VaultOutput",
    "VaultEntry",
    # ATLAS
    "GPV",
    # Metabolic state
    "EnergyState",
    "MetabolismState",
    "DecisionState",
    "EMD",
    "ScarWeight",
    # Bundles
    "DeltaBundle",
    "OmegaBundle",
    "PsiSeal",
    "SystemState",
    "Profile",
    # EUREKA Layer 1 — Score Provenance
    "ScoreComponent",
    "ScoreProvenance",
    # EUREKA Layer 6 — Reality Feedback
    "OutcomeStatus",
    "OutcomeRecord",
]
