"""\narifosmcp/runtime/contracts.py — Unified arifOS MCP Contracts\n\nUnified contract surface:\n  - Basic 11-mega-tool registry from public_registry\n  - Stage/trinity/floor maps for governance\n  - Hardened constitutional contracts (v4 additions: ToolEnvelope, OutputPolicy, VerdictScope, etc.)\n\nUPGRADE (2026-03-25 — Paris Weather Incident):\n  - OutputPolicy enum: forces model surface behaviour when domain payload is absent\n  - DRY_RUN poison pill: any dry_run=True envelope forces SIMULATION_ONLY policy\n  - Domain payload gate: DOMAIN_PAYLOAD_GATES defines required keys per domain class\n  - Verdict namespace split: ROUTER_SEAL vs DOMAIN_SEAL vs SESSION_SEAL\nSee: 000/FLOORS/F02_TRUTH.md §Enforcement Addendum (v2026.03.25)\n"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .public_registry import public_tool_names, CANONICAL_PUBLIC_TOOLS, EXPECTED_TOOL_COUNT

# ═══════════════════════════════════════════════════════════════════════════════
# 12-TOOL CONTRACT ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════════════════

_import_time_names = frozenset(public_tool_names())
_expected_names = CANONICAL_PUBLIC_TOOLS

assert len(_import_time_names) == EXPECTED_TOOL_COUNT, (
    f"CRITICAL: contracts.py sees {len(_import_time_names)} tools, "
    f"expected {EXPECTED_TOOL_COUNT}. Registry drift detected!"
)
assert _import_time_names == _expected_names, (
    f"CRITICAL: Tool name mismatch in contracts.py.\n"
    f"Expected: {sorted(_expected_names)}\n"
    f"Got: {sorted(_import_time_names)}"
)

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL SURFACES
# ═══════════════════════════════════════════════════════════════════════════════

AAA_PUBLIC_TOOLS: tuple[str, ...] = public_tool_names()

AAA_CANONICAL_TOOLS: tuple[str, ...] = AAA_PUBLIC_TOOLS

REQUIRES_SESSION: frozenset[str] = frozenset(
    {
        "arifOS_kernel",
        "agi_mind",
        "asi_heart",
        "apex_soul",
        "vault_ledger",
        "engineering_memory",
        "physics_reality",
        "math_estimator",
        "code_engine",
        "architect_registry",
        "compat_probe",
    }
)

READ_ONLY_TOOLS: set[str] = {
    "physics_reality",
    "math_estimator",
    "architect_registry",
    "compat_probe",
}

# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE METADATA
# ═══════════════════════════════════════════════════════════════════════════════

AAA_TOOL_STAGE_MAP: dict[str, str] = {
    "init_anchor": "000_INIT",
    # "anchor_session": "000_INIT",  # LEGACY: use init_anchor
    "arifOS_kernel": "444_ROUTER",
    "metabolic_loop": "444_ROUTER",
    "apex_soul": "888_JUDGE",
    "apex_judge": "888_JUDGE",
    "vault_ledger": "999_VAULT",
    "seal_vault": "999_VAULT",
    "vault_seal": "999_VAULT",
    "agi_mind": "333_MIND",
    "reason_mind": "333_MIND",
    "agi_reason": "333_MIND",
    "asi_heart": "666_HEART",
    "asi_simulate": "666_HEART",
    "asi_critique": "666_HEART",
    "engineering_memory": "555_MEMORY",
    "physics_reality": "111_SENSE",
    "math_estimator": "444_ROUTER",
    "code_engine": "M-3_EXEC",
    "architect_registry": "M-4_ARCH",
    "compat_probe": "M-5_COMPAT",
}

TRINITY_BY_TOOL: dict[str, str] = {
    "init_anchor": "PSI Ψ",
    "arifOS_kernel": "DELTA/PSI",
    "apex_soul": "PSI Ψ",
    "vault_ledger": "PSI Ψ",
    "agi_mind": "DELTA Δ",
    "asi_heart": "OMEGA Ω",
    "engineering_memory": "OMEGA Ω",
    "physics_reality": "DELTA Δ",
    "math_estimator": "DELTA Δ",
    "code_engine": "ALL",
    "architect_registry": "DELTA Δ",
    "compat_probe": "ALL",
}

AAA_TOOL_ALIASES: dict[str, str] = {
    "init": "init_anchor",
    "revoke": "init_anchor",
    "kernel": "arifOS_kernel",
    "status": "status",
    "judge": "apex_soul",
    "seal": "vault_ledger",
    "reason": "agi_mind",
}

TOOL_MODES: dict[str, frozenset[str]] = {
    "init_anchor": frozenset({"init", "state", "revoke", "refresh"}),
    "arifOS_kernel": frozenset({"kernel", "status"}),
    "apex_soul": frozenset({"judge", "rules", "validate", "hold", "armor", "notify", "probe"}),
    "vault_ledger": frozenset({"seal", "verify", "resolve"}),
    "agi_mind": frozenset({"reason", "reflect", "forge"}),
    "asi_heart": frozenset({"critique", "simulate"}),
    "engineering_memory": frozenset(
        {"engineer", "write", "vector_query", "vector_store", "vector_forget", "generate", "query"}
    ),
    "physics_reality": frozenset({"search", "ingest", "compass", "atlas", "time"}),
    "math_estimator": frozenset({"cost", "health", "vitals", "entropy"}),
    "code_engine": frozenset({"fs", "process", "net", "tail", "replay"}),
    "architect_registry": frozenset({"register", "list", "read"}),
}

AAA_TOOL_LAW_BINDINGS: dict[str, list[str]] = {
    "init_anchor": ["F11_AUTHORITY", "F12_DEFENSE", "F13_SOVEREIGNTY"],
    "arifOS_kernel": ["F4_CLARITY", "F11_AUTHORITY"],
    "apex_soul": ["F3_TRI_WITNESS", "F12_DEFENSE", "F13_SOVEREIGNTY"],
    "vault_ledger": ["F1_AMANAH", "F13_SOVEREIGNTY"],
    "agi_mind": ["F2_TRUTH", "F4_CLARITY", "F7_HUMILITY", "F8_GENIUS"],
    "asi_heart": ["F5_PEACE2", "F6_EMPATHY", "F9_ANTI_HANTU"],
    "engineering_memory": ["F11_AUTHORITY", "F2_TRUTH"],
    "physics_reality": ["F2_TRUTH", "F3_TRI_WITNESS"],
    "math_estimator": ["F4_CLARITY", "F5_PEACE2"],
    "code_engine": [],
    "architect_registry": [],
}

LAW_13_CATALOG: dict[str, dict[str, str]] = {
    "F1_AMANAH": {"name": "Amanah", "type": "floor"},
    "F2_TRUTH": {"name": "Truth", "type": "floor"},
    "F3_TRI_WITNESS": {"name": "Tri-Witness", "type": "mirror"},
    "F4_CLARITY": {"name": "Clarity", "type": "floor"},
    "F5_PEACE2": {"name": "Peace2", "type": "floor"},
    "F6_EMPATHY": {"name": "Empathy", "type": "floor"},
    "F7_HUMILITY": {"name": "Humility", "type": "floor"},
    "F8_GENIUS": {"name": "Genius", "type": "mirror"},
    "F9_ANTI_HANTU": {"name": "Dark", "type": "floor"},
    "F10_ONTOLOGY_LOCK": {"name": "Ontology", "type": "floor"},
    "F11_AUTHORITY": {"name": "Authority", "type": "floor"},
    "F12_DEFENSE": {"name": "Injection", "type": "floor"},
    "F13_SOVEREIGNTY": {"name": "Sovereign", "type": "wall"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# HARDENED CONSTITUTIONAL CONTRACTS (v4 additions)
# ═══════════════════════════════════════════════════════════════════════════════


class ToolStatus(str, Enum):
    OK = "ok"
    HOLD = "hold"
    VOID = "void"
    ERROR = "error"
    SABAR = "sabar"


class OutputPolicy(str, Enum):
    """
    F2/F7 enforcement: controls what the model surface is ALLOWED to assert.

    REAL_DOMAIN   — domain payload verified; factual claims permitted.
    SIMULATION_ONLY — result is DRY_RUN; model MUST label any answer as
                      'Estimate Only / Simulated'. Never present domain values as real.
    CANNOT_COMPUTE  — required domain payload keys absent; model MUST answer
                      'Cannot Compute — required domain payload absent.'
                      Never substitute training data or memory.
    ROUTER_META     — this is a routing/meta decision only; no domain facts released.
    """

    REAL_DOMAIN = "REAL_DOMAIN"
    SIMULATION_ONLY = "SIMULATION_ONLY"
    CANNOT_COMPUTE = "CANNOT_COMPUTE"
    ROUTER_META = "ROUTER_META"


class VerdictScope(str, Enum):
    """
    Fix 3 — Verdict namespace split.
    Prevents ROUTER_SEAL from blessing domain factual claims.

    ROUTER_SEAL  — internal routing decision is consistent. Does NOT authorise
                   domain claims about the real world.
    DOMAIN_SEAL  — domain payload has Earth evidence + required keys. Factual
                   claims are permitted for this result.
    SESSION_SEAL — anchor session is valid and active.
    DRY_RUN_SEAL — simulation completed. No real execution or domain data.
    DOMAIN_VOID  — required domain payload keys are missing. Cannot Compute.
    """

    ROUTER_SEAL = "ROUTER_SEAL"
    DOMAIN_SEAL = "DOMAIN_SEAL"
    SESSION_SEAL = "SESSION_SEAL"
    DRY_RUN_SEAL = "DRY_RUN_SEAL"
    DOMAIN_VOID = "DOMAIN_VOID"


# F2 — Required payload keys per domain class.
# If a tool returns a domain result missing ANY of these keys,
# the envelope must be CANNOT_COMPUTE / DOMAIN_VOID.
DOMAIN_PAYLOAD_GATES: dict[str, list[str]] = {
    "weather": ["temp_c", "provider", "timestamp", "location"],
    "finance": ["price", "ticker", "source", "timestamp"],
    "health": ["metric", "value", "unit", "source"],
    "code_exec": ["stdout", "exit_code", "execution_id"],
    "search": ["results", "source_urls", "query_echo"],
    "geography": ["lat", "lon", "place_name", "source"],
}


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SOVEREIGN = "sovereign"


class HumanDecisionMarker(str, Enum):
    MACHINE_RECOMMENDATION_ONLY = "machine_recommendation_only"
    HUMAN_CONFIRMATION_REQUIRED = "human_confirmation_required"
    HUMAN_APPROVAL_BOUND = "human_approval_bound"
    SEALED = "sealed"


class SessionClass(str, Enum):
    OBSERVE = "observe"
    ADVISE = "advise"
    EXECUTE = "execute"
    SOVEREIGN = "sovereign"


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    parent_trace_id: str | None
    stage_id: str
    policy_version: str
    session_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "stage_id": self.stage_id,
            "policy_version": self.policy_version,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
        }


@dataclass
class EntropyBudget:
    ambiguity_score: float = 0.0
    contradiction_count: int = 0
    delta_s: float = 0.0
    confidence: float = 0.0

    def is_stable(self) -> bool:
        if self.ambiguity_score > 0.9:
            return False
        return self.delta_s <= 0 and self.confidence >= 0.80

    def to_dict(self) -> dict[str, Any]:
        return {
            "ambiguity_score": round(self.ambiguity_score, 4),
            "contradiction_count": self.contradiction_count,
            "delta_s": round(self.delta_s, 4),
            "confidence": round(self.confidence, 4),
            "is_stable": self.is_stable(),
        }


def check_domain_gate(domain_class: str, payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    F2 domain payload gate.
    Returns (passed: bool, missing_keys: list[str]).
    If passed is False, caller must set OutputPolicy.CANNOT_COMPUTE.
    """
    required = DOMAIN_PAYLOAD_GATES.get(domain_class, [])
    missing = [k for k in required if k not in payload]
    return (len(missing) == 0), missing


@dataclass
class ToolEnvelope:
    status: ToolStatus
    tool: str
    session_id: str
    risk_tier: RiskTier
    confidence: float = 0.0
    human_decision: HumanDecisionMarker = HumanDecisionMarker.MACHINE_RECOMMENDATION_ONLY
    requires_human: bool = False
    integrity_hash: str = ""
    trace: TraceContext | None = None
    entropy: EntropyBudget = field(default_factory=EntropyBudget)
    authority: Any | None = None
    auth_context: Any | None = None
    caller_state: str | None = None
    allowed_next_tools: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    output_policy: OutputPolicy = OutputPolicy.REAL_DOMAIN
    verdict_scope: VerdictScope = VerdictScope.ROUTER_SEAL
    dry_run: bool = False

    def seal_envelope(self) -> None:
        if self.dry_run or self.payload.get("dry_run") is True:
            self.dry_run = True
            self.output_policy = OutputPolicy.SIMULATION_ONLY
            self.verdict_scope = VerdictScope.DRY_RUN_SEAL
            self.status = ToolStatus.OK
            self.warnings.append(
                "DRY_RUN=True: this result is a simulation. "
                "No domain values (weather, finance, health, code output) are real. "
                "Model MUST label any answer referencing this as 'Estimate Only / Simulated'."
            )
        data_to_hash = {
            "payload": self.payload,
            "trace": self.trace.to_dict() if self.trace else {},
            "tool": self.tool,
            "session_id": self.session_id,
            "output_policy": self.output_policy.value,
            "verdict_scope": self.verdict_scope.value,
        }
        self.integrity_hash = hashlib.sha256(
            json.dumps(data_to_hash, sort_keys=True, default=str).encode()
        ).hexdigest()

    def apply_domain_gate(self, domain_class: str) -> None:
        passed, missing = check_domain_gate(domain_class, self.payload)
        if not passed:
            self.output_policy = OutputPolicy.CANNOT_COMPUTE
            self.verdict_scope = VerdictScope.DOMAIN_VOID
            self.status = ToolStatus.VOID
            self.warnings.append(
                f"DOMAIN_GATE_FAIL [{domain_class}]: missing keys {missing}. "
                "Model MUST answer: 'Cannot Compute — required domain payload absent.' "
                "Do NOT substitute training data or memory."
            )
        else:
            self.output_policy = OutputPolicy.REAL_DOMAIN
            self.verdict_scope = VerdictScope.DOMAIN_SEAL

    def to_dict(self) -> dict[str, Any]:
        self.seal_envelope()
        return {
            "status": self.status.value,
            "tool": self.tool,
            "session_id": self.session_id,
            "risk_tier": self.risk_tier.value,
            "confidence": round(self.confidence, 4),
            "human_decision": self.human_decision.value,
            "integrity_hash": self.integrity_hash,
            "trace": self.trace.to_dict() if self.trace else None,
            "entropy": self.entropy.to_dict(),
            "payload": self.payload,
            "output_policy": self.output_policy.value,
            "verdict_scope": self.verdict_scope.value,
            "dry_run": self.dry_run,
            "warnings": self.warnings,
        }

    @classmethod
    def hold(
        cls,
        tool: str,
        session_id: str,
        reason: str,
        trace: TraceContext | None = None,
        **kwargs: Any,
    ) -> ToolEnvelope:
        payload = {"reason": reason}
        payload.update(kwargs)
        return cls(
            status=ToolStatus.HOLD,
            tool=tool,
            session_id=session_id,
            risk_tier=RiskTier.HIGH,
            requires_human=True,
            trace=trace,
            payload=payload,
            human_decision=HumanDecisionMarker.HUMAN_CONFIRMATION_REQUIRED,
        )

    @classmethod
    def void(
        cls,
        tool: str,
        session_id: str,
        reason: str,
        trace: TraceContext | None = None,
        **kwargs: Any,
    ) -> ToolEnvelope:
        payload = {"reason": reason}
        payload.update(kwargs)
        return cls(
            status=ToolStatus.VOID,
            tool=tool,
            session_id=session_id,
            risk_tier=RiskTier.LOW,
            trace=trace,
            payload=payload,
            human_decision=HumanDecisionMarker.MACHINE_RECOMMENDATION_ONLY,
        )


class _ValidationResult:
    """Return type for validate_fail_closed — preserves .valid + .to_envelope() interface."""

    def __init__(self, valid: bool, tool: str, session_id: str | None) -> None:
        self.valid = valid
        self._tool = tool
        self._session_id = session_id or "anonymous"

    def __bool__(self) -> bool:
        return self.valid

    def to_envelope(self, tool: str, session_id: str | None, trace=None):
        from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict

        return RuntimeEnvelope(
            ok=False,
            tool=tool,
            session_id=session_id or "anonymous",
            stage="000_INIT",
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": "Validation failed: auth_context, risk_tier, or session_id missing"},
        )


def validate_fail_closed(
    auth_context: dict | None,
    risk_tier: str | None,
    session_id: str | None,
    tool: str,
    trace: TraceContext | None = None,
) -> "_ValidationResult":
    valid = bool(auth_context and risk_tier and session_id)
    return _ValidationResult(valid=valid, tool=tool, session_id=session_id)


def calculate_entropy_budget(
    ambiguity_score: float, confidence: float, input_len: int = 0, output_len: int = 0
) -> EntropyBudget:
    return EntropyBudget(
        ambiguity_score=ambiguity_score, delta_s=output_len - input_len, confidence=confidence
    )


def generate_trace_context(
    stage_id: str,
    session_id: str,
    policy_version: str = "v2026.03.24-hardened",
    parent_trace_id: str | None = None,
) -> TraceContext:
    return TraceContext(
        trace_id=f"trace-{secrets.token_hex(16)}",
        parent_trace_id=parent_trace_id,
        stage_id=stage_id,
        policy_version=policy_version,
        session_id=session_id,
    )


def determine_human_marker(
    risk_tier: RiskTier, confidence: float, blast_radius: str = "minimal"
) -> HumanDecisionMarker:
    if risk_tier == RiskTier.SOVEREIGN or blast_radius in ("significant", "catastrophic"):
        return HumanDecisionMarker.HUMAN_APPROVAL_BOUND
    if risk_tier == RiskTier.HIGH or confidence < 0.80:
        return HumanDecisionMarker.HUMAN_CONFIRMATION_REQUIRED
    return HumanDecisionMarker.MACHINE_RECOMMENDATION_ONLY


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION & CONTRACT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def require_session(tool: str, session_id: str | None) -> dict[str, Any] | None:
    if tool in REQUIRES_SESSION and (not session_id or not str(session_id).strip()):
        return {
            "verdict": "HOLD",
            "stage": "F11_AUTH",
            "floors_failed": ["F11"],
            "error": "Missing session_id",
            "next_actions": [
                "Call init_anchor with mode='init' first.",
            ],
        }
    return None


def public_tool_input_contracts() -> dict[str, Any]:
    return {}


def verify_contract() -> dict[str, Any]:
    checks = {
        "tool_count": len(AAA_PUBLIC_TOOLS) == 11,
        "stage_map": len(AAA_TOOL_STAGE_MAP) >= 11,
        "trinity_map": len(TRINITY_BY_TOOL) == 11,
        "mode_map": len(TOOL_MODES) == 11,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "tools": list(AAA_PUBLIC_TOOLS),
    }


__all__ = [
    # Basic contract items
    "AAA_PUBLIC_TOOLS",
    "AAA_CANONICAL_TOOLS",
    "REQUIRES_SESSION",
    "READ_ONLY_TOOLS",
    "AAA_TOOL_STAGE_MAP",
    "TRINITY_BY_TOOL",
    "AAA_TOOL_ALIASES",
    "TOOL_MODES",
    "AAA_TOOL_LAW_BINDINGS",
    "LAW_13_CATALOG",
    "require_session",
    "public_tool_input_contracts",
    "verify_contract",
    # Hardened items (v4)
    "ToolStatus",
    "RiskTier",
    "HumanDecisionMarker",
    "SessionClass",
    "TraceContext",
    "EntropyBudget",
    "ToolEnvelope",
    "validate_fail_closed",
    "calculate_entropy_budget",
    "generate_trace_context",
    "determine_human_marker",
    "OutputPolicy",
    "VerdictScope",
    "DOMAIN_PAYLOAD_GATES",
    "check_domain_gate",
]
