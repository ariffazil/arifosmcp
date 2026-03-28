from __future__ import annotations

from dataclasses import field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from arifosmcp.runtime.fastmcp_version import AuthorizationError, HAS_AUTHORIZATION_ERROR
from fastmcp.exceptions import FastMCPError, ToolError
from pydantic import BaseModel, ConfigDict, Field

from arifosmcp.core.shared.types import AuthorityLevel, Verdict


class DeltaOmegaPsi(BaseModel):
    """ΔΩΨ — The Trinity Flag System."""

    delta: float = Field(..., ge=0.0, le=1.0, description="Δ — Entropy reduction score.")
    omega: float = Field(..., ge=0.0, le=1.0, description="Ω — Human impact load (care needed).")
    psi: float = Field(..., ge=0.0, le=1.0, description="Ψ — Paradox score (unresolved tension).")


class CoolingLedgerEntry(BaseModel):
    """The immutable ancestry tree and cryptographic proof of a metabolic event."""

    entry_id: str
    session_id: str
    organ: str
    timestamp: datetime

    parent_hash: str
    self_hash: str

    entropy_before: float
    entropy_after: float
    entropy_delta: float
    landauer_violations: int

    delta: float
    omega: float
    psi: float

    witness_internal: bool
    witness_external: bool
    witness_constitutional: bool

    verdict: str
    human_ratified: bool
    apex_audited: bool
    immutable: bool = True


class ArifOSError(FastMCPError):
    """Base exception for all arifOS-related errors."""

    def __init__(
        self,
        message: str,
        fault_class: Any,
        fault_code: str,
        verdict: str,
        extra: dict[str, Any] | None = None,
        remediation: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.fault_class = fault_class
        self.fault_code = fault_code
        self.verdict = verdict
        self.extra = extra or {}
        self.remediation = remediation


class ConstitutionalViolationError(ArifOSError, AuthorizationError):
    """Raised when a Hard Constitutional Floor is breached. Results in VOID."""

    def __init__(self, message: str, floor_code: Any, extra: dict[str, Any] | None = None, remediation: dict[str, Any] | None = None):
        super().__init__(
            message=f"CONSTITUTIONAL COLLAPSE: {message}",
            fault_class="CONSTITUTIONAL",
            fault_code=str(floor_code),
            verdict="VOID",
            extra=extra,
            remediation=remediation,
        )


class InfrastructureFaultError(ArifOSError, ToolError):
    """Raised when a mechanical fault occurs. Results in 888_HOLD."""

    def __init__(self, message: str, fault_code: Any, extra: dict[str, Any] | None = None, remediation: dict[str, Any] | None = None):
        super().__init__(
            message=f"MECHANICAL FAULT: {message}",
            fault_class="MECHANICAL",
            fault_code=str(fault_code),
            verdict="888_HOLD",
            extra=extra,
            remediation=remediation,
        )


class EpistemicGapError(ArifOSError, ToolError):
    """Raised when grounding is insufficient. Results in SABAR."""

    def __init__(self, message: str, extra: dict[str, Any] | None = None, remediation: dict[str, Any] | None = None):
        super().__init__(
            message=f"EPISTEMIC GAP: {message}",
            fault_class="EPISTEMIC",
            fault_code="NO_RESULTS",
            verdict="SABAR",
            extra=extra,
            remediation=remediation,
        )


class AuthMethod(str, Enum):
    BEARER = "bearer"
    SIG_V2 = "sig_v2"
    SESSION = "session"


class BudgetTier(str, Enum):
    """Token budget tiers for MCP tools."""
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class OverflowPolicy(str, Enum):
    """Behavior when a budget is exceeded."""
    FAIL = "fail"
    TRUNCATE = "truncate"
    TRUNCATE_AND_FLAG = "truncate_and_flag"


BUDGET_MAP: dict[BudgetTier | str, int] = {
    BudgetTier.MICRO: 100,
    BudgetTier.SMALL: 300,
    BudgetTier.MEDIUM: 1000,
    BudgetTier.LARGE: 2000,
    "micro": 100,
    "small": 300,
    "medium": 1000,
    "large": 2000,
}



class AuthContext(BaseModel):
    """
    Standardized authentication context for governed tool calls (F11).
    Established in init_anchor and verified in auth_continuity.
    """

    session_id: str | None = None
    actor_id: str = "anonymous"
    authority_level: str = "anonymous"
    token_fingerprint: str | None = None
    nonce: str | None = None
    iat: int | None = None
    exp: int | None = None
    approval_scope: list[str] = Field(default_factory=list)
    parent_signature: str | None = None
    signature: str | None = None
    prev_vault_hash: str | None = None
    
    # Backward compatibility
    method: AuthMethod = AuthMethod.SESSION
    credential: str | None = Field(default=None, description="Token, signature, or session key.")
    scope: list[str] = Field(default_factory=list, description="Authorized capability scopes.")
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = Field(default=None)

    model_config = ConfigDict(extra="allow")

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

class RuntimeStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    DRY_RUN = "DRY_RUN"
    SABAR = "SABAR"


class MachineState(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class MachineIssueLabel(str, Enum):
    AUTH_BOOTSTRAP_REQUIRED = "AUTH_BOOTSTRAP_REQUIRED"
    AUTH_FAILURE = "AUTH_FAILURE"
    AUTH_TOKEN_MISSING = "AUTH_TOKEN_MISSING"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOOL_NOT_EXPOSED = "TOOL_NOT_EXPOSED"
    BOOTSTRAP_ROUTE_MISSING = "BOOTSTRAP_ROUTE_MISSING"
    DEPLOYMENT_CONFIG_ERROR = "DEPLOYMENT_CONFIG_ERROR"
    SCHEMA_INVALID = "SCHEMA_INVALID"
    INTERNAL_RUNTIME_ERROR = "INTERNAL_RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    DNS_FAIL = "DNS_FAIL"
    TLS_FAIL = "TLS_FAIL"
    WAF_BLOCK = "WAF_BLOCK"


class IntelligenceStage(str, Enum):
    EXPLORATION = "EXPLORATION"
    ENTROPY = "ENTROPY"
    EUREKA = "EUREKA"


class ExplorationState(str, Enum):
    BROAD = "BROAD"
    SCOPED = "SCOPED"
    EXHAUSTED = "EXHAUSTED"


class EntropyState(str, Enum):
    LOW = "LOW"
    MANAGEABLE = "MANAGEABLE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskClass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ClaimStatus(str, Enum):
    """Forensic status of an identity claim (F11)."""

    ANONYMOUS = "anonymous"
    CLAIMED = "claimed"
    ANCHORED = "anchored"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DEMOTED = "demoted"
    REJECTED_PROTECTED_ID = "rejected_protected_id"


class EurekaState(str, Enum):
    NONE = "NONE"
    PARTIAL = "PARTIAL"
    FORGED = "FORGED"


class Stage(str, Enum):
    INIT_000 = "000_INIT"
    SENSE_111 = "111_SENSE"
    REALITY_222 = "222_REALITY"
    MIND_333 = "333_MIND"
    ROUTER_444 = "444_ROUTER"
    MEMORY_555 = "555_MEMORY"
    HEART_666 = "666_HEART"
    CRITIQUE_666 = "666_CRITIQUE"
    FORGE_777 = "777_FORGE"
    NEGOTIATE_800 = "800_NEGOTIATE"
    JUDGE_888 = "888_JUDGE"
    VAULT_999 = "999_VAULT"


class StageContract(BaseModel):
    """The Law of the Stage: Rules for metabolic transitions."""
    stage: Stage
    allowed_tools: list[str]
    mandatory_floors: list[str]
    valid_verdicts: list[Verdict]
    exit_criteria: str


CANONICAL_STAGE_CONTRACTS: dict[Stage, StageContract] = {
    Stage.INIT_000: StageContract(
        stage=Stage.INIT_000,
        allowed_tools=["init_anchor"],
        mandatory_floors=["F11"],
        valid_verdicts=[Verdict.ALIVE, Verdict.PROVISIONAL, Verdict.HOLD, Verdict.SEAL],
        exit_criteria="Anchored identity (session_id != 'global')."
    ),
    Stage.SENSE_111: StageContract(
        stage=Stage.SENSE_111,
        allowed_tools=["physics_reality", "math_estimator"],
        mandatory_floors=["F2", "F4"],
        valid_verdicts=[Verdict.PROVISIONAL, Verdict.SABAR],
        exit_criteria="Environmental data ingested."
    ),
    Stage.REALITY_222: StageContract(
        stage=Stage.REALITY_222,
        allowed_tools=["physics_reality", "engineering_memory"],
        mandatory_floors=["F2", "F10"],
        valid_verdicts=[Verdict.PROVISIONAL, Verdict.SABAR, Verdict.HOLD],
        exit_criteria="Truth-grounded state established."
    ),
    Stage.ROUTER_444: StageContract(
        stage=Stage.ROUTER_444,
        allowed_tools=["arifOS_kernel"],
        mandatory_floors=["F11", "F12"],
        valid_verdicts=[Verdict.PROVISIONAL, Verdict.HOLD, Verdict.VOID, Verdict.SEAL],
        exit_criteria="Directed reasoning path."
    ),
    Stage.MIND_333: StageContract(
        stage=Stage.MIND_333,
        allowed_tools=["agi_mind", "physics_reality", "engineering_memory"],
        mandatory_floors=["F2", "F4", "F7", "F8"],
        valid_verdicts=[Verdict.PROVISIONAL, Verdict.SABAR, Verdict.HOLD, Verdict.SEAL],
        exit_criteria="Grounded hypotheses with G★ > 0.70."
    ),
    Stage.HEART_666: StageContract(
        stage=Stage.HEART_666,
        allowed_tools=["asi_heart"],
        mandatory_floors=["F5", "F6", "F9"],
        valid_verdicts=[Verdict.PROVISIONAL, Verdict.HOLD, Verdict.VOID, Verdict.SEAL],
        exit_criteria="Non-destructive consequence prediction (Peace² >= 1.0)."
    ),
    Stage.JUDGE_888: StageContract(
        stage=Stage.JUDGE_888,
        allowed_tools=["apex_soul"],
        mandatory_floors=["F3", "F12", "F13"],
        valid_verdicts=[Verdict.SEAL, Verdict.HOLD, Verdict.VOID],
        exit_criteria="Human or Consensus ratification."
    ),
    Stage.VAULT_999: StageContract(
        stage=Stage.VAULT_999,
        allowed_tools=["vault_ledger"],
        mandatory_floors=["F1", "F13"],
        valid_verdicts=[Verdict.SEAL],
        exit_criteria="Immutable Merkle chain commit."
    ),
}


class SacredStage(str, Enum):
    """Canonical Sacred Names for the Inner Ring stages."""

    INIT_ANCHOR = "INIT·ANCHOR"
    AGI_REASON = "AGI·REASON"
    AGI_REFLECT = "AGI·REFLECT"
    ASI_SIMULATE = "ASI·SIMULATE"
    ASI_CRITIQUE = "ASI·CRITIQUE"
    AGI_ASI_FORGE = "AGI–ASI·FORGE"
    APEX_JUDGE = "APEX·JUDGE"
    VAULT_SEAL = "VAULT·SEAL"


class PNSSignal(BaseModel):
    """A single signal from a Peripheral Nervous System (PNS) organ."""

    source: str
    status: str = "OK"
    score: float = 1.0
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PNSContext(BaseModel):
    """
    The Peripheral Nervous System (PNS) Context — The Outer Ring.

    This context feeds the Sacred Chain (Inner Ring) at specific injection points.
    It must never contaminate the forbidden zones (SIMULATE, VAULT).
    """

    shield: PNSSignal | None = None  # Feeds INIT·ANCHOR
    search: PNSSignal | None = None  # Feeds AGI·REASON
    vision: PNSSignal | None = None  # Feeds AGI·REFLECT
    health: PNSSignal | None = None  # Feeds ASI·CRITIQUE
    floor: PNSSignal | None = None  # Feeds ASI·CRITIQUE
    orchestrate: PNSSignal | None = None  # Feeds AGI–ASI·FORGE
    redteam: PNSSignal | None = None  # Feeds APEX·JUDGE

    # Metadata
    entropy_sanitized: bool = False
    pns_version: str = "1.0.0"

    def get_signal(self, organ_name: str) -> PNSSignal | None:
        """Helper to retrieve a signal by name."""
        return getattr(self, organ_name.lower(), None)

class PersonaRole(str, Enum):
    """AI self-declared operational roles - governed whitelist."""

    ARCHITECT = "architect"
    ENGINEER = "engineer"
    AUDITOR = "auditor"
    VALIDATOR = "validator"
    ASSISTANT = "assistant"


class TelemetryVitals(BaseModel):
    """Rule 3: The Public Score Card — Sovereign Vitals."""
    ds: float = Field(0.0, description="ΔS: Entropy Delta (Landauer derivation). High dS blocks Forge (F4).")
    peace2: float = Field(1.0, description="Peace²: Lyapunov Stability. Low Peace blocks Execute (F5).")
    kappa_r: float | None = Field(None, description="κᵣ: Maruah/Empathy Score. Low score raises Hold (F6).")
    G_star: float = Field(0.0, description="G★: Genius/Coherence Score. <0.80 blocks Forge (F8).")
    echo_debt: float = Field(0.0, description="Historical Contradictions. Measured from VAULT999 (F5).")
    shadow: float = Field(0.0, description="Hidden Assumption Load. Inferred from Grounding gaps (F9).")
    confidence: float = Field(0.0, description="Ω₀: Confidence (Gödel-bounded). High Ω0 requires Hold (F7).")
    psi_le: str = Field("0.0 (Estimate Only)", description="Ψ_LE: Emergence Pressure. Forensic trace only.")
    verdict: str = Field("Alive", description="System-level vitality state.")
    # Hard Budgeting & Telemetry (V2)
    token_usage: int = Field(0, description="Total tokens consumed in this tool call.")
    requested_max_tokens: int = 0
    actual_output_tokens: int = 0
    input_tokens: int = 0
    truncated: bool = False
    overflow_policy: str = "truncate"  # Default fallback
    budget_tier: str = "medium"
    escalated_from_tier: str | None = None
    phase_token_usage: dict[str, int] = field(default_factory=dict)


class TelemetryBasis(BaseModel):
    """Rule 1: Basis tracking for every vital sign + Operational Weight."""

    ds: dict[str, str] = Field(
        default_factory=lambda: {
            "source": "derived",
            "formula": "ΔS = k * ln(W_after/W_before)",
            "enforcement": "Hard (F4): Blocks destructive entropic drift.",
        }
    )
    peace2: dict[str, str] = Field(
        default_factory=lambda: {
            "source": "derived",
            "formula": "dV/dt: Lyapunov first-order stability",
            "enforcement": "Soft (F5): Advisory during analysis, Hard during execution.",
        }
    )
    G_star: dict[str, str] = Field(
        default_factory=lambda: {
            "source": "derived",
            "formula": "G★ = (Truth * Coherence * Grounding)^1/3",
            "enforcement": "Hard (F8): Blocks hallunicated/unstable forging.",
        }
    )
    confidence: dict[str, str] = Field(
        default_factory=lambda: {
            "source": "derived",
            "formula": "Ω₀: Calibrated probability relative to uncertainty band",
            "enforcement": "Hard (F7): Forces 888_HOLD on overconfidence.",
        }
    )
    psi_le: str = "heuristic (Symbolic Only - No Enforcement)"


class TripleWitness(BaseModel):
    """The Tri-Witness block for F3 compliance."""

    human: float = 0.0
    ai: float = 0.0
    earth: float = 0.0


class CanonicalMetrics(BaseModel):
    """Unified arifOS Telemetry (Score Integrity Protocol)."""
    telemetry: TelemetryVitals = Field(default_factory=TelemetryVitals)
    basis: TelemetryBasis = Field(default_factory=TelemetryBasis)
    witness: TripleWitness = Field(default_factory=TripleWitness)

    # Internal Metadata (Operator Only)
    internal: dict[str, Any] = Field(default_factory=dict)

    @property
    def truth(self) -> float:
        return self.telemetry.G_star

    @property
    def peace(self) -> float:
        return self.telemetry.peace2

    @property
    def confidence(self) -> float:
        return self.telemetry.confidence

    @property
    def entropy_delta(self) -> float:
        return self.telemetry.ds

    model_config = ConfigDict(populate_by_name=True)

class CanonicalAuthority(BaseModel):
    actor_id: str = "anonymous"
    level: AuthorityLevel = AuthorityLevel.ANONYMOUS
    claim_status: ClaimStatus = ClaimStatus.ANONYMOUS
    human_required: bool = False
    approval_scope: list[str] = Field(default_factory=list)
    auth_state: str = "unverified"


class CanonicalError(BaseModel):
    code: str
    message: str
    stage: str | None = None
    recoverable: bool = True
    required_next_tool: str | None = None
    required_fields: list[str] | None = None
    example_next_call: dict[str, Any] | None = None
    remediation: dict[str, Any] | None = None


class CanonicalMeta(BaseModel):
    schema_version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    debug: bool = False
    dry_run: bool = False
    motto: str | None = None
    deprecation: dict[str, Any] | None = None


class PersonaId(str, Enum):
    """
    Governed AI operational personas. F9-compliant: honest naming, no sovereign claim.

    Scar-Weight Theory (W_beban):
    — Each persona carries a specific burden to protect the system.
    — Disagreement by design ensures constitutional coverage.
    — Human (888 Judge) resolves irreconcilable conflicts.

    Trinity Mapping:
        AGI Mind (Δ):  ARCHITECT + ENGINEER → "Should & Can"
        ASI Heart (Ω): AUDITOR → "What could break"
        APEX Soul (Ψ): VALIDATOR + ORCHESTRATOR → "Is it true & In what order"

    Scars (Burdens):
        ARCHITECT: Accountability jangka panjang | "Should this exist?"
        ENGINEER: Pager scars, outages | "Can we make it work?"
        AUDITOR: "Batu api" reputation | "What could break / be abused?"
        VALIDATOR: Approval pressure | "Is it actually true / correct?"
    """

    ARCHITECT = "architect"
    ENGINEER = "engineer"
    AUDITOR = "auditor"
    VALIDATOR = "validator"


class RuntimeRole(str, Enum):
    """AI runtime role within the current call."""

    ASSISTANT = "assistant"
    ROUTER = "router"
    TOOL_BROKER = "tool_broker"
    EVALUATOR = "evaluator"


class ToolchainRole(str, Enum):
    """Position of the AI agent in a multi-agent toolchain."""

    ORCHESTRATOR = "orchestrator"
    LEAF = "leaf"
    SUBAGENT = "subagent"


class UserModelSource(str, Enum):
    """Allowed provenance sources for bounded user-model fields."""

    EXPLICIT = "explicit"
    OBSERVABLE = "observable"
    DEFAULT_POLICY = "default_policy"
    UNKNOWN = "unknown"


class AdaptationMode(str, Enum):
    """Governed adaptation scope for runtime user modeling."""

    BEHAVIORAL_ONLY = "behavioral_only"


class UserModelField(BaseModel):
    """Single user-model field with provenance and bounded evidence."""

    value: Any | None = None
    source: UserModelSource = UserModelSource.UNKNOWN
    evidence: str | None = None


class InferencePolicy(BaseModel):
    """Explicit anti-Theory-of-Mind guardrails for runtime adaptation."""

    psychological_inference: str = "disallowed"
    behavioral_adaptation: str = "allowed"
    null_for_unknown: bool = True
    source_priority: list[UserModelSource] = Field(
        default_factory=lambda: [
            UserModelSource.EXPLICIT,
            UserModelSource.OBSERVABLE,
            UserModelSource.DEFAULT_POLICY,
        ]
    )


class UserModel(BaseModel):
    """
    Bounded user-model contract.

    The runtime may adapt to explicit asks and observable interaction signals,
    but must not attribute hidden motives or psychological states.
    """

    stated_goal: UserModelField | None = None
    behavioral_constraints: list[UserModelField] = Field(default_factory=list)
    output_constraints: list[UserModelField] = Field(default_factory=list)
    requested_tone: UserModelField | None = None
    expertise_level: UserModelField | None = None
    emotion_state: UserModelField | None = None
    hidden_motive: UserModelField | None = None
    adaptation_mode: AdaptationMode = AdaptationMode.BEHAVIORAL_ONLY
    inference_policy: InferencePolicy = Field(default_factory=InferencePolicy)


class CallerContext(BaseModel):
    """
    AI execution identity layer — instrument only, never sovereign (F9/F10).

    Populated by the MCP server from transport metadata. The LLM may submit a
    ``requested_persona`` hint; the server governs the final ``persona_id``.
    """

    agent_id: str | None = Field(default=None, description="Stable runtime instance ID.")
    model_id: str | None = Field(default=None, description="Model/version string.")
    persona_id: PersonaId = Field(
        default=PersonaId.ENGINEER,
        description="Governed operational persona. Server-assigned; LLM hint only.",
    )
    runtime_role: RuntimeRole = Field(
        default=RuntimeRole.ASSISTANT,
        description="Operational role for this call.",
    )
    toolchain_role: ToolchainRole = Field(
        default=ToolchainRole.LEAF,
        description="Position in multi-agent/tool chain.",
    )
    # Forward-compatible extension slot
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class RuntimeEnvelope(BaseModel):
    ok: bool = True
    tool: str
    canonical_tool_name: str | None = None
    risk_class: RiskClass = RiskClass.LOW
    requires_auth: bool = False
    requires_human: bool = False
    recoverable: bool = True
    next_action: dict[str, Any] | None = None  # Anti-chaos: exact next step
    sabar_step: str | None = None  # SABAR protocol: exact cooling / de-escalation step
    state_transition: str | None = None
    
    # Anti-chaos: caller state visibility (Phase 1)
    caller_state: str = "anonymous"  # anonymous|claimed|anchored|verified|scoped|approved
    allowed_next_tools: list[str] = Field(default_factory=list)
    blocked_tools: list[dict[str, str]] = Field(default_factory=list)  # [{tool, reason}]
    diagnostics_only: bool = False  # True for global session

    session_id: str | None = None
    stage: str
    verdict: Verdict = Verdict.SABAR
    status: RuntimeStatus = RuntimeStatus.SUCCESS
    machine_status: MachineState = MachineState.READY
    machine_issue: MachineIssueLabel | None = None
    intelligence_stage: IntelligenceStage | None = None
    intelligence_state: dict[str, Any] = Field(
        default_factory=lambda: {
            # 3E Schema: Exploration → Entropy → Eureka
            "exploration": "BROAD",
            "entropy": "MANAGEABLE",
            "eureka": "NONE",
            "hypotheses": [],
            "unknowns": [],
            "stable_facts": [],
            "unstable_assumptions": [],
            "conflicts": [],
            "uncertainty_score": 0.5,  # F7 Humility Band
            "insight": None,
            "confidence": 0.0,
            "decision_required": [],
        }
    )
    metrics: CanonicalMetrics = Field(default_factory=lambda: CanonicalMetrics())
    trace: dict[str, Any] = Field(default_factory=dict)
    authority: CanonicalAuthority = Field(default_factory=CanonicalAuthority)
    payload: dict[str, Any] = Field(default_factory=dict)
    errors: list[CanonicalError] = Field(default_factory=list)
    meta: CanonicalMeta = Field(default_factory=CanonicalMeta)
    auth_context: AuthContext | None = Field(default=None)
    caller_context: CallerContext | None = Field(
        default=None,
        description="AI execution identity. Auto-populated by MCP server.",
    )
    user_model: UserModel | None = Field(
        default=None,
        description=(
            "Bounded user model built from explicit asks and observable constraints only. "
            "Psychological inference is disallowed by policy."
        ),
    )
    philosophy: dict[str, Any] | None = Field(
        default=None,
        description="Optional governed quote layer selected by APEX-G.",
    )
    debug: dict[str, Any] | None = None
    model_config = ConfigDict(extra="allow")

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


# Rebuild models after all forward references are resolved
RuntimeEnvelope.model_rebuild()
