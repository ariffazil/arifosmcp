from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite
from typing import Any

from .thresholds import AuthorityLevel, GovernanceState, GovernanceThresholds
from .thermo_integration import THERMODYNAMICS_AVAILABLE, get_thermodynamic_budget
from .transitions import GovernanceTransitions

logger = logging.getLogger(__name__)


@dataclass
class GovernanceKernel(GovernanceTransitions):
    """Unified kernel state object (Psi)."""

    entropy_manager: Any | None = field(default=None, repr=False)
    thermodynamic_state: Any | None = field(default=None)

    authority_level: AuthorityLevel = AuthorityLevel.ANALYSIS
    decision_owner: str = "ai"

    safety_omega: float = 0.0
    display_omega: float = 0.0
    entropic_drift: float = 0.01
    uncertainty_components: dict[str, float] = field(default_factory=dict)

    irreversibility_index: float = 0.0
    reversibility_score: float = 1.0
    current_energy: float = 1.0

    # Granular life energy (Metabolic counters)
    tokens_consumed: int = 0
    reason_cycles: int = 0
    tool_calls: int = 0

    governance_state: GovernanceState = GovernanceState.ACTIVE
    governance_reason: str = "initialized"
    escalation_required: bool = False

    human_approval_status: str = "not_required"
    human_override_timestamp: float | None = None

    IRREVERSIBILITY_THRESHOLD: float = 0.6
    UNCERTAINTY_THRESHOLD: float = 0.06
    ENERGY_THRESHOLD: float = 0.2
    CONDITIONAL_UNCERTAINTY_THRESHOLD: float = 0.03

    timestamp: float = field(default_factory=time.time)
    last_transition_at: float = field(default_factory=time.time)
    last_verified_at: datetime | None = None
    last_verified_latency_ms: float | None = None
    session_id: str = ""
    earth_witness_score: float = 1.0

    # P0 HARDENING: Temporal Metrics
    metabolic_flux: float = 0.0
    epistemic_temp: float = 0.0
    temporal_jitter: float = 0.0

    @property
    def temporal_stability(self) -> float:
        if self.last_verified_latency_ms and self.last_verified_latency_ms > 0:
            dt = self.last_verified_latency_ms / 1000.0
        else:
            dt = time.time() - self.last_transition_at

        if dt > 0:
            self.metabolic_flux = self.tokens_consumed / dt

        max_flux = 500.0
        max_jitter = 50.0

        flux_p = min(1.0, self.metabolic_flux / max_flux) if self.metabolic_flux > 0 else 0.0
        jitter_p = min(1.0, self.temporal_jitter / max_jitter) if self.temporal_jitter > 0 else 0.0

        stability = 1.0 - (0.6 * flux_p + 0.4 * jitter_p)

        if dt < 0.001 and self.tokens_consumed > 10:
            stability *= 0.1

        return max(0.0, min(1.0, stability))

    def __post_init__(self) -> None:
        self.current_energy = self._clamp_unit(self.current_energy, field_name="current_energy")
        self.safety_omega = self._clamp_unit(self.safety_omega, field_name="safety_omega")
        self.display_omega = self._clamp_unit(self.display_omega, field_name="display_omega")

        if (
            THERMODYNAMICS_AVAILABLE
            and self.thermodynamic_state is None
            and get_thermodynamic_budget is not None
        ):
            try:
                self.thermodynamic_state = get_thermodynamic_budget(self.session_id)
            except Exception:
                self.thermodynamic_state = None

    @property
    def thresholds(self) -> GovernanceThresholds:
        return GovernanceThresholds(
            irreversibility_hold=self.IRREVERSIBILITY_THRESHOLD,
            uncertainty_hold=self.UNCERTAINTY_THRESHOLD,
            uncertainty_conditional=self.CONDITIONAL_UNCERTAINTY_THRESHOLD,
            energy_hold=self.ENERGY_THRESHOLD,
            max_tokens=100000,
            max_reason_cycles=10,
            max_tool_calls=50,
        )

    @property
    def energy(self) -> dict[str, Any]:
        return {
            "current_energy": round(self.current_energy, 4),
            "thermodynamic_state": (
                self.thermodynamic_state.to_dict()
                if self.thermodynamic_state and hasattr(self.thermodynamic_state, "to_dict")
                else None
            ),
            "irreversibility_index": round(self.irreversibility_index, 4),
            "reversibility_score": round(self.reversibility_score, 4),
            "human_approval_status": self.human_approval_status,
            "metabolic_usage": {
                "tokens": self.tokens_consumed,
                "reason_cycles": self.reason_cycles,
                "tool_calls": self.tool_calls,
            },
        }

    @staticmethod
    def _clamp_unit(value: float, *, field_name: str) -> float:
        if not isfinite(value):
            raise ValueError(f"{field_name} must be a finite number")
        return max(0.0, min(1.0, float(value)))

    def can_proceed(self) -> bool:
        return self.governance_state in {GovernanceState.ACTIVE, GovernanceState.CONDITIONAL}

    def get_output_tags(self) -> list[str]:
        tags: list[str] = []
        if self.authority_level == AuthorityLevel.ANALYSIS:
            tags.append("[ANALYSIS]")
        elif self.authority_level == AuthorityLevel.SUGGESTION:
            tags.append("[SUGGESTION]")
        elif self.authority_level == AuthorityLevel.REQUIRES_HUMAN:
            tags.append("[REQUIRES_HUMAN_JUDGMENT]")
        elif self.authority_level == AuthorityLevel.UNSAFE_TO_AUTOMATE:
            tags.append("[UNSAFE_TO_AUTOMATE]")

        if self.governance_state == GovernanceState.AWAITING_888:
            tags.append("[PENDING_888_APPROVAL]")
        return tags

    def architecture_map(self) -> dict[str, Any]:
        return {
            "stack": "000->999",
            "boundaries": {
                "core": "decision logic only",
                "aaa_mcp": "transport/protocol only",
                "aclip_cai": "triad intelligence backends",
            },
            "stages": {
                "000": {"name": "INIT", "floors": ["F11", "F12"]},
                "111-333": {"name": "AGI_MIND", "floors": ["F2", "F4", "F7", "F8"]},
                "444-666": {"name": "ASI_HEART", "floors": ["F1", "F5", "F6"]},
                "777-888": {"name": "APEX_SOUL", "floors": ["F3", "F9", "F10", "F13"]},
                "999": {"name": "VAULT", "floors": ["F1", "F3"]},
            },
            "runtime": {
                "state": self.governance_state.value,
                "authority": self.authority_level.value,
                "reason": self.governance_reason,
            },
        }

    @property
    def hysteresis_penalty(self) -> float:
        try:
            from arifosmcp.core.telemetry import get_current_hysteresis

            return get_current_hysteresis()
        except ImportError:
            return 0.0

    def _project_genius_floor_scores(self) -> Any:
        from arifosmcp.core.enforcement.genius import coerce_floor_scores

        return coerce_floor_scores(
            defaults={
                "f1_amanah": round(self.reversibility_score, 4),
                "f2_truth": round(max(0.0, 1.0 - self.safety_omega), 4),
                "f3_earth_witness": self.earth_witness_score,
                "f4_clarity": 0.99 if self.governance_state == GovernanceState.ACTIVE else 0.1,
                "f5_peace": round(self.reversibility_score, 4),
                "f6_empathy": 0.95,
                "f7_humility": round(0.04 - (self.safety_omega / 10.0), 4),
                "f8_genius": 0.8,
                "f11_command_auth": self.authority_level != AuthorityLevel.ANALYSIS,
                "f13_sovereign": 1.0
                if (self.human_approval_status == "approved" or self.decision_owner == "arif")
                else 0.7,
            }
        )

    def _project_genius_budget_window(self) -> tuple[float, float]:
        from arifosmcp.core.enforcement.genius import get_thermodynamic_budget_window

        return get_thermodynamic_budget_window(
            self.session_id,
            fallback_used=1.0 - self.current_energy,
            fallback_max=1.0,
        )

    @property
    def genius_score(self) -> float:
        from arifosmcp.core.enforcement.genius import calculate_genius

        floors = self._project_genius_floor_scores()
        budget_used, budget_max = self._project_genius_budget_window()
        res = calculate_genius(
            floors=floors,
            h=self.hysteresis_penalty,
            compute_budget_used=budget_used,
            compute_budget_max=budget_max,
        )
        return res["genius_score"]

    def apply_temporal_grounding(self, context: dict[str, Any]) -> None:
        """
        Hardens the kernel by aligning metrics with the temporal baseline.
        Resolves the 'no attribute' error in downstream estimators.
        """
        now = time.time()
        dt = now - self.last_transition_at

        # 1. Update Metabolic Flux
        if dt > 0:
            self.metabolic_flux = self.tokens_consumed / dt

        # 2. Update Temporal Jitter based on latency
        latency = getattr(context, "request_latency_ms", self.last_verified_latency_ms or 0.0)
        if self.last_verified_latency_ms:
            self.temporal_jitter = abs(latency - self.last_verified_latency_ms)

        # 3. Anchoring reinforcement
        if dt > 3600:  # 1 hour stale
            self.entropic_drift += 0.05
            logger.warning(
                f"Kernel [{self.session_id}] session anchor drift detected. Enforcing re-verification."
            )

        self.last_transition_at = now
        self.last_verified_at = datetime.now()
        self.last_verified_latency_ms = latency

        logger.info(
            f"Temporal grounding applied: flux={self.metabolic_flux:.2f}, jitter={self.temporal_jitter:.2f}"
        )

    def get_current_state(self) -> dict[str, Any]:
        from arifosmcp.core.enforcement.genius import calculate_genius
        from arifosmcp.core.shared.types import Verdict

        if self.governance_state == GovernanceState.VOID:
            verdict = Verdict.VOID.value
        elif self.governance_state == GovernanceState.AWAITING_888:
            verdict = Verdict.HOLD.value
        elif self.governance_state == GovernanceState.CONDITIONAL:
            verdict = Verdict.PARTIAL.value
        else:
            verdict = Verdict.SEAL.value

        floors = self._project_genius_floor_scores()
        budget_used, budget_max = self._project_genius_budget_window()

        telemetry_payload = {
            "entropy": {"uncertainty_score": self.safety_omega},
            "exploration": {"hypotheses": [1] * max(1, self.reason_cycles)},
            "eureka": {"detected": self.governance_state == GovernanceState.ACTIVE},
        }

        genius_res = calculate_genius(
            floors, self.hysteresis_penalty, budget_used, budget_max, telemetry=telemetry_payload
        )
        dials = genius_res["dials"]
        stability_t = self.temporal_stability

        return {
            "session_id": self.session_id,
            "verdict": verdict,
            "metabolic_stage": 888 if self.escalation_required else 333,
            "qdf": round(max(0.0, 1.0 - self.safety_omega), 4),
            "hysteresis": self.hysteresis_penalty,
            "genius": genius_res["genius_score"],
            "floors": {
                "F1": floors.f1_amanah,
                "F2": floors.f2_truth,
                "F3": floors.f3_earth_witness,
                "F4": floors.f4_clarity,
                "F7": floors.f7_humility,
                "F8": genius_res["genius_score"],
                "F11": 1.0 if floors.f11_command_auth else 0.0,
                "F13": floors.f13_sovereign,
            },
            "witness": {
                "human": floors.f13_sovereign,
                "ai": round(dials["A"], 4),
                "earth": round(self.earth_witness_score, 4),
                "shadow": round(dials["X"], 4),
                "w3_consensus": round(floors.tri_witness_consensus, 4),
            },
            "telemetry": {
                "dS": -0.1 if self.can_proceed() else 0.15,
                "peace2": round(max(0.0, self.reversibility_score), 4),
                "kappa_r": round(dials["A"], 4),
                "confidence": round(genius_res["genius_score"], 4),
                "psi_le": round(self.current_energy, 4),
                "joules": self.tokens_consumed * 0.0005,
                "metabolic_flux": round(self.metabolic_flux, 2),
                "temporal_stability": round(stability_t, 4),
                "uncertainty_score": self.safety_omega,
                "reason_cycles": self.reason_cycles,
            },
            "dials": dials,
        }
