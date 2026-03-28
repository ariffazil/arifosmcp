from __future__ import annotations
import logging
from typing import Any

from .thresholds import AuthorityLevel, GovernanceState, GovernanceThresholds
from .thermo_integration import THERMODYNAMICS_AVAILABLE, ThermodynamicBudget
from .app_manifest import (
    AppLayer,
    FloorClassification,
    FloorManifesto,
    AppManifesto,
    AppRegistry,
)
from .kernel_state import GovernanceKernel

logger = logging.getLogger(__name__)

# Global registry for singleton/session-scoped kernels
_governance_kernels: dict[str, GovernanceKernel] = {}

def get_governance_kernel(session_id: str | None = None) -> GovernanceKernel:
    """Entry point for retrieving or creating a governance kernel (Psi)."""
    sid = session_id or "default_kernel"
    existing = _governance_kernels.get(sid)
    if existing is not None:
        return existing

    if session_id:
        try:
            from arifosmcp.core.state.session_manager import session_manager

            session_kernel = session_manager.get_kernel(session_id)
            if session_kernel is not None:
                _governance_kernels[sid] = session_kernel
                return session_kernel
        except Exception:
            pass

    kernel = GovernanceKernel(session_id=sid)
    _governance_kernels[sid] = kernel
    return kernel

def clear_governance_kernel(session_id: str | None = None) -> None:
    """Compatibility clearer for tests and legacy callers."""
    if session_id is None:
        _governance_kernels.clear()
        return
    _governance_kernels.pop(session_id, None)

def route_pipeline(query: str, context: dict | None = None) -> list[str]:
    """
    Minimal metabolic router.
    Returns ordered stage plan for the kernel.
    """
    q = (query or "").lower()
    plan = ["111_SENSE", "333_MIND", "666_CRITIQUE"]

    grounding = ("search", "evidence", "source", "verify", "ground", "data")
    memory = ("recall", "remember", "memory", "vault", "history")
    safety = ("risk", "harm", "danger", "safe", "ethic", "impact")
    execute = ("run", "execute", "command", "shell", "delete", "write", "deploy")
    govern = ("law", "constitution", "authority", "approve", "judge")

    if any(k in q for k in grounding):
        plan.insert(1, "222_REALITY")

    if any(k in q for k in memory):
        if "555_MEMORY" not in plan:
            plan.insert(-1, "555_MEMORY")

    if any(k in q for k in safety):
        if "666_HEART" not in plan:
            plan.insert(-1, "666_HEART")

    if any(k in q for k in execute):
        if "777_FORGE" not in plan:
            plan.append("777_FORGE")

    if any(k in q for k in govern):
        if "888_JUDGE" not in plan:
            plan.append("888_JUDGE")

    if "777_FORGE" in plan:
        if "800_NEGOTIATE" not in plan:
            plan.insert(plan.index("777_FORGE") + 1, "800_NEGOTIATE")

    if "777_FORGE" in plan and "888_JUDGE" not in plan:
        plan.append("888_JUDGE")

    if context and context.get("force_grounding"):
        if "222_REALITY" not in plan:
            plan.insert(1, "222_REALITY")

    mode = context.get("mode", "recommend") if context else "recommend"
    if mode in ("inspect", "analyze"):
        return ["000_INIT", "333_MIND"]

    if context and context.get("human_required") or mode == "governed_execute":
        if "888_JUDGE" not in plan:
            plan.append("888_JUDGE")

    return plan

__all__ = [
    "AuthorityLevel",
    "GovernanceState",
    "GovernanceThresholds",
    "GovernanceKernel",
    "THERMODYNAMICS_AVAILABLE",
    "ThermodynamicBudget",
    "get_governance_kernel",
    "clear_governance_kernel",
    "_governance_kernels",
    "AppLayer",
    "FloorClassification",
    "FloorManifesto",
    "AppManifesto",
    "AppRegistry",
    "route_pipeline",
]
