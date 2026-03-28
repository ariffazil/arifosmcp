"""
core/organs/__init__.py — Organ Exports (Unified)

RUKUN AGI 5-Organ Kernel:
    init    → Stage 000 (Gate)
    mind    → The Mind (Stages 111-333)
    heart   → The Heart (Stages 555-666)
    soul    → The Soul (Stages 444 -> 777 EUREKA FORGE -> 888 APEX JUDGE)
    memory  → The Memory (Stage 999)

Usage:
    from arifosmcp.core.organs import init, mind, heart, soul, memory
    from arifosmcp.core.organs import init, sense, think, reason, empathize, align, sync, forge, judge, seal

Humanized aliases:
    anchor (init), feel (empathize)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

# Canonical modules (no legacy underscore names in public surface)
from arifosmcp.core.shared.types import InitOutput

from . import _1_agi as mind
from . import _2_asi as heart
from . import _3_apex as soul
from . import _4_vault as memory

# Unified interfaces
# Actions for direct use
from ._0_init import (
    AuthorityLevel,
    get_authority_name,
    init,
    requires_sovereign,
    scan_injection,
    validate_token,
    verify_auth,
)
from ._1_agi import agi, reason, sense, think
from ._2_asi import align, asi, empathize
from ._3_apex import apex, forge, judge, sync
from ._4_vault import SealRecord, seal, vault

# Humanized aliases
anchor = init
feel = empathize

__all__ = [
    # Organ modules
    "mind",
    "heart",
    "soul",
    "memory",
    # Unified interfaces
    "init",
    "agi",
    "asi",
    "apex",
    "vault",
    # Humanized aliases
    "anchor",
    "feel",
    # Actions
    "scan_injection",  # F12
    "verify_auth",  # F11
    "requires_sovereign",
    "sense",  # Stage 111
    "think",  # Stage 222
    "reason",  # Stage 333
    "empathize",  # Stage 555
    "align",  # Stage 666
    "sync",  # Stage 444
    "forge",  # Stage 777
    "judge",  # Stage 888
    "seal",  # Stage 999
    "vault",  # Unified vault interface
    # Types
    "InitOutput",
    "AuthorityLevel",
    "SealRecord",
    "validate_token",
    "get_authority_name",
]
