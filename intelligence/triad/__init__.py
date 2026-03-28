"""
arifosmcp.intelligence/triad/__init__.py — The 3 Triads of arifOS
"""

from .delta.anchor import anchor
from .delta.integrate import integrate
from .delta.reason import reason
from .delta.think import think
from .omega.align import align
from .omega.respond import respond
from .omega.validate import validate
from .psi.audit import audit
from .psi.forge import forge
from .psi.seal import seal

__all__ = [
    "anchor",
    "think",
    "reason",
    "integrate",
    "respond",
    "validate",
    "align",
    "forge",
    "audit",
    "seal",
]
