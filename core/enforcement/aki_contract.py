"""
core/enforcement/aki_contract.py — Hard Boundary Enforcement (L2 ↔ L3)

The AKI (Arif Kernel Interface) Enforcement Gate. This is the 'Hard Boundary'
that prevents internal operations (L2) from acting on the external
Civilization (L3) without explicit constitutional verification.
"""

import logging
from typing import Any

from arifosmcp.core.governance_kernel import GovernanceKernel

logger = logging.getLogger(__name__)


class AKIContract:
    """
    The 'Wall' between Operation and Civilization.
    Enforces the L2 <-> L3 boundary contract.
    """

    def __init__(self, kernel: GovernanceKernel):
        self.kernel = kernel

    def validate_material_action(self, tool_id: str, payload: dict[str, Any]) -> bool:
        """
        Hard Enforcement: No tool can bypass this gate.
        Returns: True if action is 'Signed as Lawful', False if VOID.
        """
        # 1. F11/F13: Authority Check
        from arifosmcp.core.governance_kernel import AuthorityLevel

        if self.kernel.authority_level == AuthorityLevel.UNSAFE_TO_AUTOMATE:
            logger.error(f"AKI VOID: Tool {tool_id} blocked. Authority level UNSAFE.")
            return False

        # 2. F2: Truth Check (Uncertainty)
        if self.kernel.safety_omega > self.kernel.UNCERTAINTY_THRESHOLD:
            logger.warning(
                f"AKI VOID: Tool {tool_id} blocked. "
                f"Uncertainty (Ω₀={self.kernel.safety_omega:.3f}) too high."
            )
            return False

        # 3. F4/F5: Thermodynamic/Stability Check (System Heat)
        # If peace^2 < 1.0 (reversibility low) and energy is low, block.
        if self.kernel.reversibility_score < 0.5 and self.kernel.current_energy < 0.3:
            logger.warning(
                f"AKI HOLD: Tool {tool_id} blocked. System heat too high "
                f"(Reversibility: {self.kernel.reversibility_score:.2f})."
            )
            return False

        # 4. F11 + F13: Sovereignty Check (High-stakes / Irreversibility)
        if self.kernel.irreversibility_index > self.kernel.IRREVERSIBILITY_THRESHOLD:
            if self.kernel.human_approval_status != "approved":
                logger.warning(
                    f"AKI HOLD: Tool {tool_id} requires 888 ratification. "
                    f"(Index: {self.kernel.irreversibility_index:.3f})"
                )
                return False

        # 5. L2-L3 Boundary Enforcement (Phoenix Protocol States)
        from arifosmcp.core.governance_kernel import GovernanceState

        if self.kernel.governance_state == GovernanceState.QUARANTINED:
            logger.error(f"AKI QUARANTINE: Tool {tool_id} blocked. System is in QUARANTINED state.")
            return False

        if self.kernel.governance_state == GovernanceState.DEGRADED:
            # Degraded mode only allowed read-only operations
            safe_prefix = ("read", "get", "list", "search", "check", "audit")
            if not any(tool_id.startswith(p) for p in safe_prefix):
                logger.warning(f"AKI DEGRADED: Non-safe tool {tool_id} blocked in DEGRADED mode.")
                return False

        logger.info(
            f"AKI SEAL: Tool {tool_id} signed as lawful (Session: {self.kernel.session_id})."
        )
        return True

    def ingest_feedback(self, result: Any):
        """
        Implementation of the [L3 -> STATE] feedback law.
        Updates the kernel's state field after a tool returns from Civilization.
        """
        # This would decrease 'Void' (uncertainty) and consume 'Energy'
        # In this mock, we just log the transition.
        logger.info("AKI FEEDBACK: World data updating State Field (Ψ).")
        pass


# Example usage for a mock tool router
def invoke_governed_tool(kernel: GovernanceKernel, tool_id: str, payload: dict[str, Any]):
    aki = AKIContract(kernel)
    if aki.validate_material_action(tool_id, payload):
        # Proceed with execution in L3 Civilization
        pass
    else:
        # Trigger 888_HOLD or VOID
        pass


# =========================================================================
# L2 <-> L3 SOVEREIGN GATES (Migrated from 333_APPS/metabolizer.py)
# =========================================================================


class SovereignGate:
    """
    888_HOLD enforcement gate for irreversible actions.
    Any application performing destructive operations MUST pass through this gate.
    """

    IRREVERSIBLE_ACTIONS = {
        "delete",
        "remove",
        "drop",
        "truncate",
        "send",
        "transfer",
        "trade",
        "execute",
        "deploy",
        "publish",
        "commit",
        "purge",
        "terminate",
        "overwrite_law",
        "rebase",
    }

    def __init__(self, action_type: str, resource_path: str, requires_signature: bool = True):
        self.action_type = action_type.lower()
        self.resource_path = resource_path
        self.requires_signature = requires_signature
        self.is_irreversible = self.action_type in self.IRREVERSIBLE_ACTIONS

    async def check_approval(
        self, context: dict[str, Any], proposed_verdict: str = "SEAL"
    ) -> dict[str, Any]:
        """Check if action is approved or requires 888_HOLD with signature."""
        if self.is_irreversible and self.requires_signature:
            # F11: Nonce Requirement for Material Execution
            import uuid

            nonce = uuid.uuid4().hex[:8]

            return {
                "verdict": "888_HOLD",
                "output": {
                    "message": (
                        f"Action '{self.action_type}' on '{self.resource_path}' "
                        "requires sovereign approval"
                    ),
                    "action_type": self.action_type,
                    "resource": self.resource_path,
                    "authority": "888_JUDGE",
                    "ratification_token_required": True,
                    "nonce": nonce,
                    "signed_intent_envelope_required": True,
                },
                "stage": "888_HOLD",
            }
        return {
            "verdict": proposed_verdict,
            "output": {"approved": True, "action": self.action_type},
            "stage": "pre-flight",
        }

    def verify_signature(self, signature: str, nonce: str | None = None) -> bool:
        """
        Verifies the human/L0-kernel signature.
        In production, this should check HMAC or RSA signature of (nonce + resource).
        """
        # Canonical 'SEAL' bypass for dev; production requires proper crypto
        if signature.upper() == "SEAL":
            return True
        return False


class L0KernelGatekeeper:
    """Protects L0_KERNEL from modification by L1-L7 apps."""

    PROTECTED_PATHS = [
        "000_THEORY/000_LAW.md",
        "core/enforcement/floors.py",
        "core/enforcement/aki_contract.py",
        "core/shared/floors.py",
        "333_APPS/L0_CONSTITUTION/",
        "T000_VERSIONING.md",
        "pyproject.toml",
        "arifosmcp/runtime/bridge.py",
        "core/kernel/",
    ]

    @classmethod
    def check_modification_permission(cls, filepath: str) -> bool:
        normalized_path = filepath.replace("\\", "/")
        for protected in cls.PROTECTED_PATHS:
            if protected in normalized_path or normalized_path.endswith(protected):
                return False
        return True

    @classmethod
    def assert_modification_allowed(cls, filepath: str) -> None:
        if not cls.check_modification_permission(filepath):
            raise PermissionError(
                f"🚫 SOVEREIGN ONLY: Cannot modify '{filepath}'. "
                f"Modification of L0_KERNEL constitutional law requires 888_JUDGE authority. "
            )
