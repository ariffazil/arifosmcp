"""
core/recovery/rollback_engine.py — Governance State Restoration & Reality Feedback

Provides:
1. RollbackEngine — repair/rollback GovernanceKernel to a healthy checkpoint.
2. OutcomeLedger  — post-action reality feedback loop (EUREKA Layer 6).
   Records decision → action → outcome triples, reconciles predicted vs
   observed risk, and adjusts per-actor trust scores accordingly.
"""

import copy
import json
import logging
import time
from pathlib import Path
from typing import Any

from arifosmcp.core.governance_kernel import GovernanceKernel
from arifosmcp.core.shared.types import OutcomeRecord, OutcomeStatus

_DEFAULT_OUTCOMES_PATH = Path(__file__).parents[2] / "VAULT999" / "outcomes.jsonl"

logger = logging.getLogger(__name__)


class RollbackEngine:
    """
    Constitutional State Repair.
    Ensures that truth remains immutable even if reasoning fails.
    """

    def __init__(self):
        self._checkpoints: dict[str, list[GovernanceKernel]] = {}
        self._max_history = 5

    def create_checkpoint(self, session_id: str, kernel: GovernanceKernel):
        """Save a snapshot of the current governance state."""
        if session_id not in self._checkpoints:
            self._checkpoints[session_id] = []

        # Perform deep copy to ensure isolation
        snapshot = copy.deepcopy(kernel)
        self._checkpoints[session_id].append(snapshot)

        # Keep only the last N checkpoints
        if len(self._checkpoints[session_id]) > self._max_history:
            self._checkpoints[session_id].pop(0)

    def rollback(self, session_id: str) -> GovernanceKernel | None:
        """
        Restore the kernel to the previous healthy checkpoint.
        Use this when HomeostaticCollapse exception is raised.
        """
        if session_id not in self._checkpoints or not self._checkpoints[session_id]:
            logger.error(f"No checkpoints found for session {session_id}. Rollback failed.")
            return None

        # The last checkpoint is the current failing state, so take the one before it
        if len(self._checkpoints[session_id]) >= 2:
            self._checkpoints[session_id].pop()  # Remove current bad state
            healthy_state = self._checkpoints[session_id][-1]
            logger.info(f"Session {session_id} rolled back to previous checkpoint.")
            return copy.deepcopy(healthy_state)

        return None


# Global singleton
rollback_engine = RollbackEngine()


# =============================================================================
# EUREKA Layer 6 — Reality Feedback / Post-Action Accountability
# =============================================================================

# Trust score policy parameters — named constants for tuneability
DEFAULT_TRUST = 0.70  # Starting trust score for unknown actors
TRUST_PENALTY_HARM = -0.10  # Harm event significantly erodes trust
TRUST_PENALTY_OVERRIDE = -0.02  # Human override suggests mild policy disagreement
TRUST_REWARD_SUCCESS = 0.02  # Trust accretes slowly through consistent good outcomes


class OutcomeLedger:
    """
    Immutable record of decision → action → outcome triples.

    Answers the question every governance system must face:
    *"What actually happened after the decision?"*

    Features:
    - Record predicted outcomes at decision time.
    - Resolve outcomes as observations arrive post-action.
    - Reconcile predicted vs observed risk to measure calibration error.
    - Adjust per-actor trust scores based on outcome history.
    - Feed real attack traces back into adversarial test suites.

    Usage::

        ledger = OutcomeLedger()
        rec = ledger.record_outcome(
            decision_id="DEC-001", session_id="sess-1",
            verdict_issued="SEAL", expected_outcome="safe file classification"
        )
        # ... action executes ...
        ledger.resolve_outcome("DEC-001", actual_outcome="metadata leak", harm_detected=True)
        metrics = ledger.reconcile()
    """

    def __init__(self, persist_path: Path = _DEFAULT_OUTCOMES_PATH) -> None:
        self._records: list[OutcomeRecord] = []
        self._trust_scores: dict[str, float] = {}  # actor_id → trust [0.0, 1.0]
        self._persist_path = persist_path

    # ------------------------------------------------------------------
    # Persistence (EUREKA Layer 6 — Cross-Session Feedback)
    # ------------------------------------------------------------------

    def _save_record(self, record: OutcomeRecord) -> None:
        """Append a single OutcomeRecord to the durable outcomes ledger."""
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._persist_path, "a", encoding="utf-8") as fh:
                fh.write(record.model_dump_json() + "\n")
        except Exception as e:
            logger.warning("OutcomeLedger: failed to persist record %s: %s", record.decision_id, e)

    def load_recent(self, n: int = 10) -> list[OutcomeRecord]:
        """Read the last *n* OutcomeRecords from disk (newest-last order)."""
        if not self._persist_path.exists():
            return []
        try:
            lines = self._persist_path.read_text(encoding="utf-8").splitlines()
            recent: list[OutcomeRecord] = []
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                try:
                    recent.append(OutcomeRecord(**json.loads(line)))
                except Exception:
                    continue
                if len(recent) >= n:
                    break
            return list(reversed(recent))
        except Exception as e:
            logger.warning("OutcomeLedger: failed to load recent records: %s", e)
            return []

    def build_scar_context(self, n: int = 10) -> dict[str, Any]:
        """
        Summarise the last *n* persisted outcomes into a scar_context dict
        suitable for injection into the 000_ANCHOR InitOutput.

        Keys:
            total        — number of records examined
            harm_count   — how many caused observed harm
            pending      — how many are still PENDING (no real consequence observed)
            false_seals  — SEAL decisions that later showed harm
            last_id      — decision_id of the most recent record
        """
        records = self.load_recent(n)
        if not records:
            return {"total": 0, "harm_count": 0, "pending": 0, "false_seals": 0, "last_id": None}

        harm_count = sum(1 for r in records if r.harm_detected)
        pending = sum(1 for r in records if r.outcome_status == OutcomeStatus.PENDING)
        false_seals = sum(
            1 for r in records if r.verdict_issued == "SEAL" and r.harm_detected
        )
        return {
            "total": len(records),
            "harm_count": harm_count,
            "pending": pending,
            "false_seals": false_seals,
            "last_id": records[-1].decision_id,
        }

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_outcome(
        self,
        decision_id: str,
        session_id: str,
        verdict_issued: str,
        expected_outcome: str,
        actual_outcome: str = "",
        harm_detected: bool = False,
        reversible: bool = True,
        operator_override: bool = False,
        override_reason: str = "",
        floor_attribution: dict[str, float] | None = None,
    ) -> OutcomeRecord:
        """
        Record a governance decision with its expected outcome.

        Call at decision time (before execution).  Resolve later with
        :meth:`resolve_outcome` once the real-world result is known.
        """
        has_result = bool(actual_outcome)
        if has_result:
            status = (
                OutcomeStatus.OVERRIDDEN
                if operator_override
                else OutcomeStatus.FAILURE
                if harm_detected
                else OutcomeStatus.SUCCESS
            )
        else:
            status = OutcomeStatus.PENDING

        record = OutcomeRecord(
            decision_id=decision_id,
            session_id=session_id,
            verdict_issued=verdict_issued,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            outcome_status=status,
            harm_detected=harm_detected,
            reversible=reversible,
            operator_override=operator_override,
            override_reason=override_reason,
            timestamp_decision=str(time.time()),
            floor_attribution=floor_attribution or {},
        )
        self._records.append(record)
        self._save_record(record)
        logger.debug("OutcomeLedger: recorded decision %s → %s", decision_id, verdict_issued)
        return record

    def resolve_outcome(
        self,
        decision_id: str,
        actual_outcome: str,
        harm_detected: bool = False,
        operator_override: bool = False,
        override_reason: str = "",
    ) -> OutcomeRecord | None:
        """
        Update a PENDING outcome record with the observed real-world result.

        Call once the action has executed and the result is known.
        """
        for r in self._records:
            if r.decision_id == decision_id and r.outcome_status == OutcomeStatus.PENDING:
                r.actual_outcome = actual_outcome
                r.harm_detected = harm_detected
                r.operator_override = operator_override
                r.override_reason = override_reason
                r.timestamp_outcome = str(time.time())
                r.outcome_status = (
                    OutcomeStatus.OVERRIDDEN
                    if operator_override
                    else OutcomeStatus.FAILURE
                    if harm_detected
                    else OutcomeStatus.SUCCESS
                )
                self._save_record(r)
                logger.info(
                    "OutcomeLedger: resolved %s → %s (harm=%s)",
                    decision_id,
                    r.outcome_status,
                    harm_detected,
                )
                return r
        return None

    def get_outcomes(self, session_id: str | None = None) -> list[OutcomeRecord]:
        """Return all records, optionally filtered by session_id."""
        if session_id:
            return [r for r in self._records if r.session_id == session_id]
        return list(self._records)

    # ------------------------------------------------------------------
    # Reality Reconciliation
    # ------------------------------------------------------------------

    def reconcile(self) -> dict[str, Any]:
        """
        Reality Reconciliation: compute calibration error across resolved outcomes.

        Metrics returned:

        - ``resolved``         — count of non-PENDING records
        - ``false_seal_rate``  — SEAL decisions that caused harm
        - ``false_void_rate``  — VOID/888_HOLD decisions later overridden as safe
        - ``override_rate``    — fraction overridden by a human operator
        - ``harm_rate``        — overall fraction that caused observed harm
        """
        resolved = [r for r in self._records if r.outcome_status != OutcomeStatus.PENDING]
        if not resolved:
            return {
                "resolved": 0,
                "false_seal_rate": 0.0,
                "false_void_rate": 0.0,
                "override_rate": 0.0,
                "harm_rate": 0.0,
            }

        seals = [r for r in resolved if r.verdict_issued == "SEAL"]
        voids = [r for r in resolved if r.verdict_issued in ("VOID", "888_HOLD")]
        overrides = [r for r in resolved if r.operator_override]

        false_seals = [r for r in seals if r.harm_detected]
        false_voids = [r for r in voids if r.operator_override and not r.harm_detected]

        return {
            "resolved": len(resolved),
            "false_seal_rate": round(len(false_seals) / len(seals), 4) if seals else 0.0,
            "false_void_rate": round(len(false_voids) / len(voids), 4) if voids else 0.0,
            "override_rate": round(len(overrides) / len(resolved), 4),
            "harm_rate": round(sum(1 for r in resolved if r.harm_detected) / len(resolved), 4),
        }

    # ------------------------------------------------------------------
    # Trust Adjustment
    # ------------------------------------------------------------------

    def update_trust(self, actor_id: str, outcome: OutcomeRecord) -> float:
        """
        Adjust the trust score for *actor_id* based on *outcome*.

        Policy parameters (module-level constants):
        - ``TRUST_PENALTY_HARM``     → significant trust erosion on observed harm
        - ``TRUST_PENALTY_OVERRIDE`` → mild erosion on human policy override
        - ``TRUST_REWARD_SUCCESS``   → slow trust accretion on clean success

        Trust is clamped to ``[0.0, 1.0]``.  New actors start at ``DEFAULT_TRUST``.
        """
        current = self._trust_scores.get(actor_id, DEFAULT_TRUST)
        if outcome.harm_detected:
            delta = TRUST_PENALTY_HARM
        elif outcome.operator_override and not outcome.harm_detected:
            delta = TRUST_PENALTY_OVERRIDE
        else:
            delta = TRUST_REWARD_SUCCESS

        new_trust = max(0.0, min(1.0, current + delta))
        self._trust_scores[actor_id] = new_trust
        logger.info("Trust update %s: %.3f → %.3f", actor_id, current, new_trust)
        return new_trust

    def get_trust(self, actor_id: str) -> float:
        """Return the current trust score for *actor_id* (default ``DEFAULT_TRUST``)."""
        return self._trust_scores.get(actor_id, DEFAULT_TRUST)


# Global singleton — used by the vault organ and pipeline
outcome_ledger = OutcomeLedger()
