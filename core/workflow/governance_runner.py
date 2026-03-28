"""
arifOS Workflow Governance Runner
=================================

Deterministic orchestration layer with machine-checkable gates.
Turns workflow-system.yaml into executable constraints.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any

import yaml


def _utcnow() -> datetime:
    """Timezone-aware UTC timestamp for governance events."""
    return datetime.now(timezone.utc)


# ============================================================================
# ENUMS
# ============================================================================


class RawStatus(Enum):
    """Raw metric status from checks."""

    PASS = auto()
    FAIL = auto()
    NOT_CHECKED = auto()


class DecisionStatus(Enum):
    """Decision status that a stage emits."""

    PROCEED = auto()  # All checks pass, continue
    CONDITIONAL = auto()  # Pass with conditions/mitigations
    HOLD = auto()  # Pause, requires external input
    RETURN = auto()  # Go back to previous stage
    VOID = auto()  # Terminate, do not proceed


class Verdict(Enum):
    """Verdict options for 888-JUDGE."""

    SEAL = auto()
    PARTIAL = auto()
    SABAR = auto()
    VOID = auto()
    HOLD = auto()


class FloorType(Enum):
    """Types of constitutional floors."""

    HARD = auto()
    SOFT = auto()
    MIRROR = auto()
    WALL = auto()
    VETO = auto()


class Severity(Enum):
    """Contradiction and risk severity levels."""

    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INFO = auto()


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class GovernanceHeader:
    """Required header for all workflow stage outputs."""

    session_id: str
    stage_id: str
    timestamp: datetime
    authority: str
    workflow_version: str = "v2026.3.6-CANON-EXECUTABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "stage_id": self.stage_id,
            "timestamp": self.timestamp.isoformat(),
            "authority": self.authority,
            "workflow_version": self.workflow_version,
        }


@dataclass
class Evidence:
    """Single piece of evidence."""

    evidence_id: str
    claim: str
    evidence_type: str
    source: str
    confidence: float  # 0.0 - 1.0
    timestamp: datetime
    supporting_data: dict | None = None

    def validate(self) -> bool:
        """Validate evidence meets minimum standards."""
        if not self.claim:
            return False
        if not 0.0 <= self.confidence <= 1.0:
            return False
        return True


@dataclass
class Contradiction:
    """Registered contradiction between claims."""

    contradiction_id: str
    conflicting_claims: list[str]
    severity: Severity
    resolution_status: str  # "UNRESOLVED", "RESOLVED", "WAIVED"
    timestamp: datetime
    resolution_notes: str | None = None

    def is_resolved(self) -> bool:
        return self.resolution_status == "RESOLVED"

    def blocks_progression(self) -> bool:
        """Critical or HIGH unresolved contradictions block."""
        return self.resolution_status == "UNRESOLVED" and self.severity in (
            Severity.CRITICAL,
            Severity.HIGH,
        )


@dataclass
class Risk:
    """Registered risk."""

    risk_id: str
    description: str
    probability: float  # 0.0 - 1.0
    impact: float  # 0.0 - 1.0
    mitigation: str
    owner: str
    status: str  # "OPEN", "MITIGATED", "ACCEPTED", "CLOSED"

    @property
    def risk_score(self) -> float:
        return self.probability * self.impact


@dataclass
class FloorCheck:
    """Result of checking a constitutional floor."""

    floor_id: str
    floor_name: str
    raw_status: RawStatus
    metric_value: float | None = None
    threshold_value: float | None = None
    notes: str = ""

    @property
    def is_pass(self) -> bool:
        """Below threshold is NEVER pass for HARD floors."""
        if self.raw_status == RawStatus.FAIL:
            return False
        if self.raw_status == RawStatus.NOT_CHECKED:
            return False

        # For metric-based floors, must meet threshold
        if self.metric_value is not None and self.threshold_value is not None:
            # F4 is MAXIMUM (delta_s <= 0)
            if self.floor_id == "F4":
                return self.metric_value <= self.threshold_value
            # F9 is MAXIMUM (c_dark < 0.30)
            elif self.floor_id == "F9":
                return self.metric_value < self.threshold_value
            # F7 is RANGE
            elif self.floor_id == "F7":
                return 0.03 <= self.metric_value <= 0.05
            # All others are MINIMUM
            else:
                return self.metric_value >= self.threshold_value

        return self.raw_status == RawStatus.PASS


@dataclass
class TransitionGate:
    """Gate controlling transition between stages."""

    from_stage: str
    to_stage: str
    decision: DecisionStatus
    timestamp: datetime
    evidence_refs: list[str]
    approval_ref: str | None = None

    def validate(self, config: WorkflowConfig) -> bool:
        """Validate transition is allowed."""
        allowed = config.get_allowed_transitions(self.from_stage)
        return self.to_stage in allowed or self.decision == DecisionStatus.VOID


@dataclass
class ApprovalRecord:
    """Human approval record."""

    approval_id: str
    approver: str
    authority_level: str
    timestamp: datetime
    scope: str
    conditions: list[str]

    def validate(self, required_level: str) -> bool:
        """Check if approval meets minimum authority."""
        hierarchy = ["GUEST", "USER", "ADMIN", "888_JUDGE"]
        approver_idx = (
            hierarchy.index(self.authority_level) if self.authority_level in hierarchy else -1
        )
        required_idx = hierarchy.index(required_level) if required_level in hierarchy else -1
        return approver_idx >= required_idx


@dataclass
class StageOutput:
    """Complete output from a workflow stage."""

    header: GovernanceHeader
    floor_checks: list[FloorCheck] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)
    decision: DecisionStatus = DecisionStatus.HOLD
    transition: TransitionGate | None = None
    metrics: dict[str, float] = field(default_factory=dict)

    def get_floor_check(self, floor_id: str) -> FloorCheck | None:
        """Get check result for specific floor."""
        for check in self.floor_checks:
            if check.floor_id == floor_id:
                return check
        return None

    def has_unresolved_contradictions(self) -> bool:
        """Check for blocking contradictions."""
        return any(c.blocks_progression() for c in self.contradictions)

    def all_floors_pass(self, required_floors: list[str]) -> bool:
        """Check if all required floors pass."""
        for floor_id in required_floors:
            check = self.get_floor_check(floor_id)
            if not check or not check.is_pass:
                return False
        return True


# ============================================================================
# WORKFLOW CONFIG
# ============================================================================


class WorkflowConfig:
    """Loaded workflow system configuration."""

    def __init__(self, config_path: Path | None = None):
        if config_path is None:
            config_path = Path(__file__).parent / "workflow-system.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def get_stage(self, stage_id: str) -> dict[str, Any]:
        """Get stage definition."""
        stages = self.config.get("stages", {})
        return stages.get(stage_id, {})

    def get_floor(self, floor_id: str) -> dict[str, Any]:
        """Get floor definition."""
        floors = self.config.get("floors", {})
        return floors.get(floor_id, {})

    def get_allowed_transitions(self, from_stage: str) -> list[str]:
        """Get allowed transitions from a stage."""
        transitions = self.config.get("transitions", {})
        stage_trans = transitions.get(from_stage, {})

        allowed = []
        if "default" in stage_trans:
            allowed.append(stage_trans["default"])
        if "alternatives" in stage_trans:
            for alt in stage_trans["alternatives"]:
                allowed.append(alt["to"])

        # Any stage can VOID
        allowed.append("VOID")

        return allowed

    def get_tool_permissions(self, stage_id: str) -> dict[str, Any]:
        """Get tool permissions for a stage."""
        perms = self.config.get("tool_permissions", {})
        stage_perms = dict(perms.get(stage_id, {}))
        allowed = list(stage_perms.get("allowed", []))
        forbidden = list(stage_perms.get("forbidden", []))

        # Hard safety default: only 999-vault may use seal_vault.
        if (
            stage_id != "999-vault"
            and "seal_vault" not in allowed
            and "seal_vault" not in forbidden
        ):
            forbidden.append("seal_vault")

        stage_perms["allowed"] = allowed
        stage_perms["forbidden"] = forbidden
        return stage_perms

    def get_validation_rules(self) -> dict[str, Any]:
        """Get validation rules."""
        return self.config.get("validation_rules", {})

    def check_tool_allowed(self, stage_id: str, tool_name: str) -> tuple[bool, str | None]:
        """Check if tool is allowed for stage. Returns (allowed, error_message)."""
        perms = self.get_tool_permissions(stage_id)

        forbidden = perms.get("forbidden", [])
        if tool_name in forbidden:
            return False, f"Tool '{tool_name}' is forbidden in stage '{stage_id}'"

        allowed = perms.get("allowed", [])
        if tool_name not in allowed:
            return False, f"Tool '{tool_name}' not in allowed list for stage '{stage_id}'"

        return True, None


# ============================================================================
# GOVERNANCE RUNNER
# ============================================================================


class GovernanceRunner:
    """Main orchestrator for workflow governance."""

    def __init__(self, config: WorkflowConfig | None = None):
        self.config = config or WorkflowConfig()
        self.session_id = str(uuid.uuid4())
        self.current_stage: str | None = None
        self.stage_history: list[StageOutput] = []
        self.ledger: list[dict] = []

    def run_stage(
        self,
        stage_id: str,
        authority: str,
        floor_results: dict[str, dict[str, Any]],
        evidence: list[Evidence],
        contradictions: list[Contradiction],
        risks: list[Risk],
        proposed_decision: DecisionStatus,
        proposed_transition: str | None = None,
        human_approval: ApprovalRecord | None = None,
    ) -> StageOutput:
        """
        Run governance checks for a stage.

        This is the core enforcement function. It validates:
        1. All required floors are checked
        2. No below-threshold metrics marked as PASS
        3. No unresolved critical contradictions
        4. Transition is allowed
        5. Human approval where required
        """

        # Create header
        header = GovernanceHeader(
            session_id=self.session_id,
            stage_id=stage_id,
            timestamp=_utcnow(),
            authority=authority,
        )

        # Convert floor results to FloorCheck objects
        floor_checks = []
        for floor_id, result in floor_results.items():
            floor_def = self.config.get_floor(floor_id)
            check = FloorCheck(
                floor_id=floor_id,
                floor_name=floor_def.get("name", floor_id),
                raw_status=RawStatus[result.get("raw_status", "NOT_CHECKED")],
                metric_value=result.get("metric_value"),
                threshold_value=result.get("threshold_value"),
                notes=result.get("notes", ""),
            )
            floor_checks.append(check)

        # Validate floor checks
        validation_errors = self._validate_floor_checks(stage_id, floor_checks)
        if validation_errors:
            raise GovernanceError(f"Floor validation failed: {validation_errors}")

        # Check contradictions
        if any(c.blocks_progression() for c in contradictions):
            if proposed_decision not in (DecisionStatus.HOLD, DecisionStatus.VOID):
                raise GovernanceError(
                    "Unresolved critical/high contradictions block progression. "
                    "Decision must be HOLD or VOID."
                )

        # Validate transition
        if proposed_transition:
            allowed = self.config.get_allowed_transitions(stage_id)
            if proposed_transition not in allowed:
                raise GovernanceError(
                    f"Transition to '{proposed_transition}' not allowed from '{stage_id}'. "
                    f"Allowed: {allowed}"
                )

        # Special stage validations
        special_errors = self._check_stage_specific_rules(stage_id, proposed_decision, floor_checks)
        if special_errors:
            raise GovernanceError(f"Stage-specific validation failed: {special_errors}")

        # Check human approval requirements
        approval_errors = self._check_approval_requirements(
            stage_id,
            proposed_decision,
            human_approval,
            proposed_transition=proposed_transition,
            floor_results=floor_results,
        )
        if approval_errors:
            raise GovernanceError(f"Approval validation failed: {approval_errors}")

        # Create transition gate
        transition = None
        if proposed_transition:
            transition = TransitionGate(
                from_stage=stage_id,
                to_stage=proposed_transition,
                decision=proposed_decision,
                timestamp=_utcnow(),
                evidence_refs=[e.evidence_id for e in evidence],
                approval_ref=human_approval.approval_id if human_approval else None,
            )

        # Build output
        output = StageOutput(
            header=header,
            floor_checks=floor_checks,
            evidence=evidence,
            contradictions=contradictions,
            risks=risks,
            decision=proposed_decision,
            transition=transition,
        )

        # Record in history
        self.stage_history.append(output)
        self.current_stage = stage_id

        # Write to ledger
        self._write_to_ledger(output)

        return output

    def _validate_floor_checks(self, stage_id: str, checks: list[FloorCheck]) -> list[str]:
        """Validate floor check results."""
        errors = []
        rules = self.config.get_validation_rules()

        # Check no below-threshold is marked PASS
        strict_floors = rules.get("below_threshold_is_not_pass", {}).get("floors", [])

        for check in checks:
            if check.floor_id in strict_floors:
                if check.raw_status == RawStatus.PASS and check.metric_value is not None:
                    # Re-check the actual threshold
                    if not check.is_pass:
                        errors.append(
                            f"{check.floor_id}: Below threshold but marked PASS. "
                            f"Metric={check.metric_value}, Threshold={check.threshold_value}"
                        )

        return errors

    def _check_approval_requirements(
        self,
        stage_id: str,
        decision: DecisionStatus,
        approval: ApprovalRecord | None,
        proposed_transition: str | None = None,
        floor_results: dict[str, dict[str, Any]] | None = None,
    ) -> list[str]:
        """Check if human approval is required and valid."""
        errors = []

        human_approval_config = self.config.config.get("human_approval", {})
        required_approvals = human_approval_config.get("required_at", [])

        for req in required_approvals:
            if req["stage"] == stage_id:
                if not self._approval_triggered(
                    req=req,
                    stage_id=stage_id,
                    decision=decision,
                    proposed_transition=proposed_transition,
                    floor_results=floor_results or {},
                ):
                    continue

                if approval is None:
                    errors.append(f"Stage '{stage_id}' requires human approval but none provided")
                else:
                    min_level = req.get("minimum_authority", "USER")
                    if not approval.validate(min_level):
                        errors.append(
                            f"Approval authority '{approval.authority_level}' insufficient. "
                            f"Required: '{min_level}'"
                        )

        return errors

    def _approval_triggered(
        self,
        req: dict[str, Any],
        stage_id: str,
        decision: DecisionStatus,
        proposed_transition: str | None,
        floor_results: dict[str, dict[str, Any]],
    ) -> bool:
        """Evaluate trigger conditions for stage-level human approval."""
        trigger = str(req.get("trigger", "")).strip().lower()

        if trigger in {"before_verdict_rendering", "before_seal"}:
            return True

        if trigger == "irreversible_action_detected":
            # Treat deployment/seal transition as irreversible by default.
            if proposed_transition in {"999-vault", "COMPLETE"}:
                return True

            # If F1 indicates failure/risk, approval is required.
            f1_result = floor_results.get("F1", {})
            if str(f1_result.get("raw_status", "")).upper() == "FAIL":
                return True

            metric = f1_result.get("metric_value")
            threshold = f1_result.get("threshold_value")
            if isinstance(metric, (int, float)) and isinstance(threshold, (int, float)):
                return float(metric) < float(threshold)

            return False

        # Unknown trigger defaults to strict behavior only for finalization stages.
        return stage_id in {"888-judge", "999-vault"}

    def _check_stage_specific_rules(
        self,
        stage_id: str,
        decision: DecisionStatus,
        floor_checks: list[FloorCheck],
    ) -> list[str]:
        """Check stage-specific validation rules."""
        errors = []
        rules = self.config.get_validation_rules()

        # 700-PROTOTYPE cannot imply production deployment
        if stage_id == "700-prototype":
            if decision == DecisionStatus.PROCEED:
                # Check if trying to deploy
                # This would be caught by transition validation (can't go to 999)
                pass

        # 888-JUDGE must have all floors pass for SEAL
        if stage_id == "888-judge":
            if decision == DecisionStatus.PROCEED:  # SEAL
                required = rules.get("all_floors_must_be_checked", {}).get("at_stages", [])
                if stage_id in required:
                    # Check all F1-F13 are checked and pass
                    floor_ids = [f"F{i}" for i in range(1, 14)]
                    check_map = {c.floor_id: c for c in floor_checks}

                    for fid in floor_ids:
                        if fid not in check_map:
                            errors.append(f"{fid} not checked (required for JUDGE)")
                        elif not check_map[fid].is_pass:
                            errors.append(f"{fid} does not pass (required for SEAL)")

        # 999-VAULT requires governance token and approval
        if stage_id == "999-vault":
            # These would be validated by _check_approval_requirements
            pass

        return errors

    def _write_to_ledger(self, output: StageOutput):
        """Write stage output to immutable ledger."""
        entry = {
            "session_id": output.header.session_id,
            "stage_id": output.header.stage_id,
            "timestamp": output.header.timestamp.isoformat(),
            "decision": output.decision.name,
            "floor_status": {
                c.floor_id: {
                    "raw": c.raw_status.name,
                    "pass": c.is_pass,
                    "metric": c.metric_value,
                }
                for c in output.floor_checks
            },
            "contradictions": [
                {
                    "id": c.contradiction_id,
                    "severity": c.severity.name,
                    "resolved": c.is_resolved(),
                }
                for c in output.contradictions
            ],
            "transition": output.transition.to_stage if output.transition else None,
        }

        # Compute hash for integrity
        entry_json = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_json.encode()).hexdigest()[:16]

        self.ledger.append(entry)

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of entire session."""
        return {
            "session_id": self.session_id,
            "current_stage": self.current_stage,
            "stages_completed": len(self.stage_history),
            "ledger_entries": len(self.ledger),
            "final_decision": self.stage_history[-1].decision.name if self.stage_history else None,
        }


class GovernanceError(Exception):
    """Exception for governance violations."""

    pass


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def create_evidence(
    claim: str,
    evidence_type: str,
    source: str,
    confidence: float,
    supporting_data: dict | None = None,
) -> Evidence:
    """Factory function to create evidence with auto-generated ID."""
    return Evidence(
        evidence_id=f"EV-{uuid.uuid4().hex[:8]}",
        claim=claim,
        evidence_type=evidence_type,
        source=source,
        confidence=confidence,
        timestamp=_utcnow(),
        supporting_data=supporting_data,
    )


def create_contradiction(
    claims: list[str],
    severity: Severity,
) -> Contradiction:
    """Factory function to create contradiction."""
    return Contradiction(
        contradiction_id=f"CN-{uuid.uuid4().hex[:8]}",
        conflicting_claims=claims,
        severity=severity,
        resolution_status="UNRESOLVED",
        timestamp=_utcnow(),
    )


def create_risk(
    description: str,
    probability: float,
    impact: float,
    mitigation: str,
    owner: str,
) -> Risk:
    """Factory function to create risk."""
    return Risk(
        risk_id=f"RK-{uuid.uuid4().hex[:8]}",
        description=description,
        probability=probability,
        impact=impact,
        mitigation=mitigation,
        owner=owner,
        status="OPEN",
    )


def create_approval(
    approver: str,
    authority_level: str,
    scope: str,
    conditions: list[str],
) -> ApprovalRecord:
    """Factory function to create approval record."""
    return ApprovalRecord(
        approval_id=f"AP-{uuid.uuid4().hex[:8]}",
        approver=approver,
        authority_level=authority_level,
        timestamp=_utcnow(),
        scope=scope,
        conditions=conditions,
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("arifOS Governance Runner")
    print("========================")

    # Initialize
    runner = GovernanceRunner()
    config = WorkflowConfig()

    print(f"Session ID: {runner.session_id}")
    print(f"Config version: {config.config['metadata']['version']}")

    # Example: Check tool permissions
    allowed, error = config.check_tool_allowed("700-prototype", "eureka_forge")
    print(f"\n700-PROTOTYPE can use eureka_forge: {allowed}")

    allowed, error = config.check_tool_allowed("700-prototype", "seal_vault")
    print(f"700-PROTOTYPE can use seal_vault: {allowed}")
    if error:
        print(f"  Error: {error}")

    print("\nGovernance system initialized and ready.")
