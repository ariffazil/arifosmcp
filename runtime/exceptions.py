"""
arifosmcp/runtime/exceptions.py — Backward compatibility shim.

All exceptions are defined in models.py. This module re-exports them
for legacy imports.
"""

from arifosmcp.runtime.models import (
    ArifOSError,
    ConstitutionalViolationError as ConstitutionalViolation,
    EpistemicGapError as EpistemicGap,
    InfrastructureFaultError as InfrastructureFault,
)

__all__ = [
    "ArifOSError",
    "ConstitutionalViolation",
    "EpistemicGap",
    "InfrastructureFault",
]
