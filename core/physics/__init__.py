"""
core/physics/ — Thermodynamic Constraints

F4 Clarity: Hardware-level entropy reduction via ZRAM/compression
F11 Command: CPU sovereignty enforcement (prevent Wallet Assassin loops)
F7 Humility: Environmental uncertainty measurement (Ω₀)

This module lives in core/ (kernel), NOT aaa_mcp/ (adapter).
Constitutional Boundary: All thermodynamic constraints enforced here.
"""

from .thermodynamics import (
    EntropyManager,
    ThermodynamicState,
    get_entropy_manager,
)

__all__ = [
    "ThermodynamicState",
    "EntropyManager",
    "get_entropy_manager",
]
