"""
arifosmcp/runtime/megaTools/__init__.py

11 Mega-Tools — Split from tools.py (2026-03-28)

Each tool is in its own file for independent auditing and testing.
"""

from .tool_01_init_anchor import init_anchor
from .tool_02_arifOS_kernel import arifOS_kernel
from .tool_03_apex_soul import apex_soul
from .tool_04_vault_ledger import vault_ledger
from .tool_05_agi_mind import agi_mind
from .tool_06_asi_heart import asi_heart
from .tool_07_engineering_memory import engineering_memory
from .tool_08_physics_reality import physics_reality
from .tool_09_math_estimator import math_estimator
from .tool_10_code_engine import code_engine
from .tool_11_architect_registry import architect_registry

MEGA_TOOLS = {
    "init_anchor": init_anchor,
    "arifOS_kernel": arifOS_kernel,
    "apex_soul": apex_soul,
    "vault_ledger": vault_ledger,
    "agi_mind": agi_mind,
    "asi_heart": asi_heart,
    "engineering_memory": engineering_memory,
    "physics_reality": physics_reality,
    "math_estimator": math_estimator,
    "code_engine": code_engine,
    "architect_registry": architect_registry,
}

__all__ = [
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
    "MEGA_TOOLS",
]
