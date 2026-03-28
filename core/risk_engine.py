"""
core/risk_engine.py — Deterministic Action Gating (Layer A)

Enforces the risk matrix for arifOS actions.
Maps intent to ActionClass and verifies thermodynamic/sovereign thresholds.
"""

import re

from arifosmcp.core.shared.types import ActionClass

# P3 Validated Thresholds
RISK_THRESHOLDS = {
    ActionClass.READ: 0.80,
    ActionClass.WRITE: 0.90,
    ActionClass.EXECUTE: 0.95,
    ActionClass.CRITICAL: 0.98,
}

DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"mkfs",
    r"dd\s+if=",
    r"> /dev/",
    r"chmod\s+-R\s+777",
    r"shutdown",
    r"reboot",
]

MODERATE_PATTERNS = [
    r"apt\s+install",
    r"pip\s+install",
    r"git\s+push",
    r"docker\s+rm",
]


class RiskEngine:
    """Deterministic layer for action gating."""

    @staticmethod
    def classify_action(command: str) -> ActionClass:
        """Classify a shell command into an ActionClass."""
        cmd_lower = command.lower()

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                return ActionClass.CRITICAL

        for pattern in MODERATE_PATTERNS:
            if re.search(pattern, cmd_lower):
                return ActionClass.EXECUTE

        if any(x in cmd_lower for x in ["mv", "cp", "touch", "mkdir", "rm", "write"]):
            return ActionClass.WRITE

        return ActionClass.READ

    @staticmethod
    def evaluate_gate(
        action_class: ActionClass, w3_score: float, verdict: str, human_ratified: bool = False
    ) -> tuple[bool, str]:
        """
        Evaluate if an action is permitted based on P3 thresholds.

        Returns: (permitted, reason)
        """
        threshold = RISK_THRESHOLDS.get(action_class, 0.99)
        # print(f"DEBUG evaluate_gate: class={action_class}, score={w3_score}, thresh={threshold}")

        if verdict == "VOID":
            return False, "Action VOIDed by constitutional floor violation."

        if w3_score < threshold:
            return (
                False,
                f"Tri-Witness Consensus {w3_score:.3f} < threshold {threshold} for {action_class}.",
            )

        if action_class == ActionClass.CRITICAL and not human_ratified:
            return False, "CRITICAL action requires explicit human ratification (888_HOLD)."

        return True, "Action permitted by Risk Engine."


risk_engine = RiskEngine()
