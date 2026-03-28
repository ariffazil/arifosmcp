"""
core/ — arifOS Kernel (2026.03.10-METABOLIC-ROUTER-SEAL)

Reusable governance engine containing ALL decision logic.
Imported by: aaa_mcp (wrapper), future products

Components:
- uncertainty_engine: 5-dim vector with harmonic/geometric mean
- governance_kernel: Conditional AWAITING_888
- telemetry: 30-day locked adaptation
- judgment: Canonical verdict interface
- organs: Six constitutional tools

Architecture: Kernel/Wrapper pattern
core/ = decision logic (this package)
aaa_mcp/ = transport only (no decisions)
"""

from __future__ import annotations

from importlib import import_module

__version__ = "2026.03.10"

__all__ = [
    "enforcement",
    "uncertainty_engine",
    "governance_kernel",
    "telemetry",
    "judgment",
    "organs",
]


def __getattr__(name: str):
    if name in __all__:
        return import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
