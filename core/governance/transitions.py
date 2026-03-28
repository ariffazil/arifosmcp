import time
import logging
from datetime import datetime
from math import isfinite
from typing import Any

from .thresholds import AuthorityLevel, GovernanceState

logger = logging.getLogger(__name__)

class GovernanceTransitions:
    """State machine logic for the governance kernel."""

    def _set_state(
        self,
        state: GovernanceState,
        authority_level: AuthorityLevel,
        reason: str,
        *,
        human_status: str | None = None,
    ) -> None:
        self.governance_state = state
        self.authority_level = authority_level
        self.governance_reason = reason
        self.escalation_required = state == GovernanceState.AWAITING_888
        self.last_transition_at = time.time()

        if human_status is not None:
            self.human_approval_status = human_status
        elif state == GovernanceState.AWAITING_888:
            self.human_approval_status = "pending"
        elif self.human_approval_status == "pending":
            self.human_approval_status = "not_required"

    def update_uncertainty(
        self,
        safety_omega: float,
        display_omega: float,
        components: dict[str, float],
    ) -> None:
        self.safety_omega = self._clamp_unit(safety_omega, field_name="safety_omega")
        self.display_omega = self._clamp_unit(display_omega, field_name="display_omega")
        self.uncertainty_components = {
            key: self._clamp_unit(float(val), field_name=f"uncertainty_components.{key}")
            for key, val in (components or {}).items()
            if isinstance(val, (float, int))
        }
        self._evaluate_governance()

    def update_irreversibility(
        self,
        impact_scope: float,
        recovery_cost: float,
        time_to_reverse: float,
    ) -> None:
        impact = self._clamp_unit(impact_scope, field_name="impact_scope")
        recovery = self._clamp_unit(recovery_cost, field_name="recovery_cost")
        time_cost = self._clamp_unit(time_to_reverse, field_name="time_to_reverse")

        self.irreversibility_index = impact * recovery * time_cost
        self.reversibility_score = max(0.0, 1.0 - self.irreversibility_index)
        self._evaluate_governance()

    def _evaluate_governance(self) -> None:
        if self.current_energy <= 0.0:
            self._set_state(
                GovernanceState.VOID,
                AuthorityLevel.UNSAFE_TO_AUTOMATE,
                "energy_depleted",
            )
            return

        if self.irreversibility_index > self.IRREVERSIBILITY_THRESHOLD:
            self._set_state(
                GovernanceState.AWAITING_888,
                AuthorityLevel.REQUIRES_HUMAN,
                "irreversibility_high",
                human_status="pending",
            )
            return

        if self.safety_omega > self.UNCERTAINTY_THRESHOLD:
            self._set_state(
                GovernanceState.AWAITING_888,
                AuthorityLevel.REQUIRES_HUMAN,
                "uncertainty_high",
                human_status="pending",
            )
            return

        if self.current_energy < self.ENERGY_THRESHOLD:
            self._set_state(
                GovernanceState.AWAITING_888,
                AuthorityLevel.REQUIRES_HUMAN,
                "energy_low",
                human_status="pending",
            )
            return

        t = self.thresholds
        if self.tokens_consumed > t.max_tokens:
            self._set_state(
                GovernanceState.VOID, AuthorityLevel.UNSAFE_TO_AUTOMATE, "token_budget_exceeded"
            )
            return
        if self.reason_cycles > t.max_reason_cycles:
            self._set_state(
                GovernanceState.AWAITING_888,
                AuthorityLevel.REQUIRES_HUMAN,
                "reason_cycle_budget_exceeded",
            )
            return
        if self.tool_calls > t.max_tool_calls:
            self._set_state(
                GovernanceState.AWAITING_888,
                AuthorityLevel.REQUIRES_HUMAN,
                "tool_call_budget_exceeded",
            )
            return

        if self.safety_omega > self.CONDITIONAL_UNCERTAINTY_THRESHOLD:
            self._set_state(
                GovernanceState.CONDITIONAL,
                AuthorityLevel.SUGGESTION,
                "uncertainty_medium",
            )
            return

        self._set_state(
            GovernanceState.ACTIVE,
            AuthorityLevel.ANALYSIS,
            "stable",
        )

    def approve_human(self, approved: bool, actor: str = "888") -> None:
        self.human_override_timestamp = time.time()
        if approved:
            self.decision_owner = actor
            if self.current_energy <= 0.0:
                self._set_state(
                    GovernanceState.VOID,
                    AuthorityLevel.UNSAFE_TO_AUTOMATE,
                    "human_approved_but_energy_depleted",
                    human_status="approved",
                )
                return

            self._set_state(
                GovernanceState.CONDITIONAL,
                AuthorityLevel.SUGGESTION,
                "human_approved",
                human_status="approved",
            )
            return

        self.decision_owner = "system"
        self._set_state(
            GovernanceState.VOID,
            AuthorityLevel.UNSAFE_TO_AUTOMATE,
            "human_denied",
            human_status="denied",
        )

    def apply_temporal_grounding(self, contract: Any) -> None:
        """
        P0: Enforce temporal contracts on kernel decisions.
        Anchors kernel to verified wall-clock and wall-latency.
        """
        from arifosmcp.core.shared.types import TemporalContract

        if not isinstance(contract, TemporalContract):
            return

        self.last_verified_at = contract.observed_at
        self.last_verified_latency_ms = contract.request_latency_ms

        if self.authority_level == AuthorityLevel.REQUIRES_HUMAN:
            # Landauer Hardening
            t_min = 1500.0
            if contract.request_latency_ms < t_min:
                reason = f"temporal_insufficiency: latency {contract.request_latency_ms}ms < {t_min}ms"
                self._set_state(GovernanceState.CONDITIONAL, AuthorityLevel.SUGGESTION, reason)

        if contract.valid_until:
            now = datetime.now(contract.valid_until.tzinfo) if contract.valid_until.tzinfo else datetime.now()
            if now > contract.valid_until:
                self._set_state(GovernanceState.VOID, AuthorityLevel.UNSAFE_TO_AUTOMATE, "authority_expired")

        self._evaluate_governance()
