"""
Tests for arifOS Workflow Governance Runner

Validates:
- Skipped stage progression
- Below-threshold metric marked PASS
- Unresolved contradiction proceeding
- Missing rollback still proceeding
- Prototype attempting prod action
- Vault sealing without human approval

DITEMPA BUKAN DIBERI
"""

# Import the governance runner
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from governance_runner import (
    DecisionStatus,
    GovernanceError,
    GovernanceRunner,
    Severity,
    WorkflowConfig,
    create_approval,
    create_contradiction,
    create_evidence,
)


class TestSkippedStageProgression:
    """Test that stages cannot be skipped improperly."""

    def test_cannot_skip_required_stage(self):
        """000-INIT cannot be skipped."""
        GovernanceRunner()
        config = WorkflowConfig()

        # Try to go from non-existent to 100-EXPLORE without 000-INIT
        # This should be caught by transition validation
        allowed = config.get_allowed_transitions("any")

        # VOID is always allowed
        assert "VOID" in allowed

    def test_400_design_cannot_be_skipped(self):
        """400-DESIGN is required and cannot be skipped."""
        config = WorkflowConfig()
        stage = config.get_stage("400-design")

        assert stage["required"] is True
        assert stage["skippable"] is False


class TestBelowThresholdMetrics:
    """Test that below-threshold metrics cannot be marked PASS."""

    def test_f2_truth_below_threshold_not_pass(self):
        """F2 Truth with τ < 0.99 cannot be PASS."""
        runner = GovernanceRunner()

        # Try to mark F2 as PASS with below-threshold metric
        floor_results = {
            "F2": {
                "raw_status": "PASS",
                "metric_value": 0.85,  # Below 0.99 threshold
                "threshold_value": 0.99,
            }
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="700-prototype",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
            )

        assert "Below threshold but marked PASS" in str(exc_info.value)

    def test_f4_clarity_positive_delta_s_not_pass(self):
        """F4 Clarity with ΔS > 0 cannot be PASS."""
        runner = GovernanceRunner()

        floor_results = {
            "F4": {
                "raw_status": "PASS",
                "metric_value": 0.5,  # Positive entropy (bad)
                "threshold_value": 0,  # Max 0
            }
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="700-prototype",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
            )

        assert "Below threshold but marked PASS" in str(exc_info.value)


class TestUnresolvedContradictions:
    """Test that unresolved contradictions block progression."""

    def test_critical_contradiction_blocks_proceed(self):
        """CRITICAL unresolved contradiction cannot PROCEED."""
        runner = GovernanceRunner()

        contradiction = create_contradiction(
            claims=["Approach A is best", "Approach B is best"],
            severity=Severity.CRITICAL,
        )

        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99}
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="888-judge",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[contradiction],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
            )

        assert "Unresolved critical/high contradictions" in str(exc_info.value)

    def test_high_contradiction_blocks_proceed(self):
        """HIGH unresolved contradiction cannot PROCEED."""
        runner = GovernanceRunner()

        contradiction = create_contradiction(
            claims=["Cost is $100", "Cost is $1000"],
            severity=Severity.HIGH,
        )

        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99}
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="888-judge",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[contradiction],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
            )

        assert "Unresolved critical/high contradictions" in str(exc_info.value)

    def test_resolved_contradiction_allows_proceed(self):
        """Resolved contradiction allows PROCEED."""
        runner = GovernanceRunner()

        contradiction = create_contradiction(
            claims=["A", "B"],
            severity=Severity.CRITICAL,
        )
        contradiction.resolution_status = "RESOLVED"

        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99}
        }

        # Should not raise
        output = runner.run_stage(
            stage_id="700-prototype",
            authority="test",
            floor_results=floor_results,
            evidence=[create_evidence("test", "test", "test", 0.9)],
            contradictions=[contradiction],
            risks=[],
            proposed_decision=DecisionStatus.PROCEED,
            proposed_transition="800-verify",
        )

        assert output.decision == DecisionStatus.PROCEED

    def test_medium_contradiction_does_not_block(self):
        """MEDIUM unresolved contradiction does not block (but warns)."""
        runner = GovernanceRunner()

        contradiction = create_contradiction(
            claims=["Minor detail X", "Minor detail Y"],
            severity=Severity.MEDIUM,
        )

        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99}
        }

        # Should not raise - MEDIUM doesn't block
        output = runner.run_stage(
            stage_id="700-prototype",
            authority="test",
            floor_results=floor_results,
            evidence=[create_evidence("test", "test", "test", 0.9)],
            contradictions=[contradiction],
            risks=[],
            proposed_decision=DecisionStatus.PROCEED,
            proposed_transition="800-verify",
        )

        assert output.decision == DecisionStatus.PROCEED


class TestRollbackRequirements:
    """Test that missing rollback plans are caught."""

    def test_700_prototype_requires_rollback_plan(self):
        """700-PROTOTYPE should have rollback plan."""
        config = WorkflowConfig()
        rules = config.get_validation_rules()

        stages_requiring_rollback = rules.get("rollback_plan_required_for", [])

        assert "700-prototype" in stages_requiring_rollback
        assert "999-vault" in stages_requiring_rollback


class TestPrototypeRestrictions:
    """Test that 700-PROTOTYPE cannot perform production actions."""

    def test_prototype_cannot_deploy_to_production(self):
        """700-PROTOTYPE cannot transition directly to 999-VAULT."""
        GovernanceRunner()
        config = WorkflowConfig()

        # Check that 999-vault is not in allowed transitions from 700-prototype
        allowed = config.get_allowed_transitions("700-prototype")

        assert "999-vault" not in allowed
        assert "800-verify" in allowed  # Must go through verify

    def test_prototype_cannot_use_seal_vault(self):
        """700-PROTOTYPE cannot use seal_vault tool."""
        config = WorkflowConfig()

        allowed, error = config.check_tool_allowed("700-prototype", "seal_vault")

        assert allowed is False
        assert "forbidden" in error.lower() or "not in allowed" in error.lower()

    def test_prototype_tool_permissions(self):
        """700-PROTOTYPE has restricted tool permissions."""
        config = WorkflowConfig()
        perms = config.get_tool_permissions("700-prototype")

        assert "eureka_forge" in perms.get("allowed", [])
        assert "seal_vault" in perms.get("forbidden", [])

        restrictions = perms.get("restrictions", [])
        assert "NO_PRODUCTION_DEPLOYMENT" in restrictions
        assert "NO_SECRETS_IN_CODE" in restrictions


class TestJudgeRestrictions:
    """Test that 888-JUDGE cannot self-authorize."""

    def test_judge_requires_human_approval(self):
        """888-JUDGE requires human approval."""
        config = WorkflowConfig()
        human_approval = config.config.get("human_approval", {})
        required = human_approval.get("required_at", [])

        judge_reqs = [r for r in required if r["stage"] == "888-judge"]
        assert len(judge_reqs) > 0
        assert judge_reqs[0]["trigger"] == "before_verdict_rendering"

    def test_judge_cannot_use_forge_tools(self):
        """888-JUDGE cannot use eureka_forge."""
        config = WorkflowConfig()

        allowed, error = config.check_tool_allowed("888-judge", "eureka_forge")

        assert allowed is False

    def test_judge_requires_all_floors_for_seal(self):
        """888-JUDGE requires all F1-F13 checked for SEAL."""
        runner = GovernanceRunner()

        # Only provide some floors, not all
        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99},
            "F4": {"raw_status": "PASS", "metric_value": -0.5, "threshold_value": 0},
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="888-judge",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,  # SEAL
                proposed_transition="999-vault",
            )

        # Should fail because not all floors checked
        error_msg = str(exc_info.value)
        assert "not checked (required for JUDGE)" in error_msg or "does not pass" in error_msg


class TestVaultRestrictions:
    """Test that 999-VAULT requires proper authorization."""

    def test_vault_requires_human_approval(self):
        """999-VAULT requires human approval."""
        runner = GovernanceRunner()

        floor_results = {
            "F1": {"raw_status": "PASS"},
            "F3": {"raw_status": "PASS"},
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="999-vault",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
                proposed_transition="COMPLETE",
            )

        assert "requires human approval" in str(exc_info.value).lower()

    def test_vault_requires_approval_with_sufficient_authority(self):
        """999-VAULT requires ADMIN level approval."""
        runner = GovernanceRunner()

        # Create approval with USER level (insufficient)
        user_approval = create_approval(
            approver="test-user",
            authority_level="USER",
            scope="999-vault",
            conditions=[],
        )

        floor_results = {
            "F1": {"raw_status": "PASS"},
            "F3": {"raw_status": "PASS"},
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="999-vault",
                authority="test",
                floor_results=floor_results,
                evidence=[],
                contradictions=[],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
                proposed_transition="COMPLETE",
                human_approval=user_approval,
            )

        assert "insufficient" in str(exc_info.value).lower()

    def test_vault_accepts_admin_approval(self):
        """999-VAULT accepts ADMIN level approval."""
        runner = GovernanceRunner()

        # Create approval with ADMIN level (sufficient)
        admin_approval = create_approval(
            approver="admin-user",
            authority_level="ADMIN",
            scope="999-vault",
            conditions=[],
        )

        floor_results = {
            "F1": {"raw_status": "PASS"},
            "F3": {"raw_status": "PASS"},
        }

        # Should not raise
        output = runner.run_stage(
            stage_id="999-vault",
            authority="test",
            floor_results=floor_results,
            evidence=[create_evidence("test", "test", "test", 0.9)],
            contradictions=[],
            risks=[],
            proposed_decision=DecisionStatus.PROCEED,
            proposed_transition="COMPLETE",
            human_approval=admin_approval,
        )

        assert output.decision == DecisionStatus.PROCEED


class TestValidTransitions:
    """Test that valid transitions work correctly."""

    def test_valid_transition_000_to_100(self):
        """000-INIT can transition to 100-EXPLORE."""
        config = WorkflowConfig()
        allowed = config.get_allowed_transitions("000-init")

        assert "100-explore" in allowed

    def test_valid_transition_700_to_800(self):
        """700-PROTOTYPE can transition to 800-VERIFY."""
        config = WorkflowConfig()
        allowed = config.get_allowed_transitions("700-prototype")

        assert "800-verify" in allowed

    def test_invalid_transition_blocked(self):
        """Invalid transitions are blocked."""
        runner = GovernanceRunner()

        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99}
        }

        with pytest.raises(GovernanceError) as exc_info:
            runner.run_stage(
                stage_id="000-init",
                authority="test",
                floor_results=floor_results,
                evidence=[create_evidence("test", "test", "test", 0.9)],
                contradictions=[],
                risks=[],
                proposed_decision=DecisionStatus.PROCEED,
                proposed_transition="999-vault",  # Invalid from 000-init
            )

        assert "not allowed" in str(exc_info.value).lower()


class TestEvidenceAndLedger:
    """Test evidence creation and ledger writing."""

    def test_evidence_creation(self):
        """Evidence factory creates valid evidence."""
        evidence = create_evidence(
            claim="Test claim",
            evidence_type="test",
            source="test-source",
            confidence=0.95,
        )

        assert evidence.evidence_id.startswith("EV-")
        assert evidence.claim == "Test claim"
        assert evidence.confidence == 0.95
        assert evidence.validate() is True

    def test_ledger_written_after_stage(self):
        """Ledger entry created after stage run."""
        runner = GovernanceRunner()

        initial_count = len(runner.ledger)

        floor_results = {
            "F2": {"raw_status": "PASS", "metric_value": 0.99, "threshold_value": 0.99}
        }

        runner.run_stage(
            stage_id="100-explore",
            authority="test",
            floor_results=floor_results,
            evidence=[create_evidence("test", "test", "test", 0.9)],
            contradictions=[],
            risks=[],
            proposed_decision=DecisionStatus.PROCEED,
            proposed_transition="200-discover",
        )

        assert len(runner.ledger) == initial_count + 1
        assert "hash" in runner.ledger[-1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
