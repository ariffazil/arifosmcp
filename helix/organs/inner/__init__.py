"""
arifosmcp/helix/organs/inner/__init__.py

Re-exports all 8 Sacred Inner Organ metabolism functions.

Digit-prefixed packages (000_anchor, 333_reason, 555_reflect, 666a_simulate)
cannot be imported via standard import syntax. importlib bridges them.
Valid-named packages (critique, forge, judge, vault) are imported directly.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import importlib as _il
from typing import Any


def _from(package: str, func: str) -> Any:
    """Load a function from a digit-prefix or valid-name organ package."""
    mod = _il.import_module(f"arifosmcp.helix.organs.inner.{package}")
    return getattr(mod, func)


# ── Inner Ring: 8 Sacred Organs ──────────────────────────────────────────────

# 000_INIT — Session anchor and constitutional frame
init_anchor_metabolism = _from("000_anchor", "init_anchor_metabolism")

# 333_MIND — Structured reasoning synthesis
agi_reason_metabolism = _from("333_reason", "agi_reason_metabolism")

# 555_MEMORY — Vault retrieval and reflection
agi_reflect_metabolism = _from("555_reflect", "agi_reflect_metabolism")

# 666A_HEART — World model consequence prediction (Forbidden Zone)
asi_simulate_metabolism = _from("666a_simulate", "asi_simulate_metabolism")

# 666B_CRITIQUE — Self-evaluation and thought audit
from arifosmcp.helix.organs.inner.critique import asi_critique_metabolism

# 777_FORGE — Solution generation and artifact synthesis
from arifosmcp.helix.organs.inner.forge import agi_asi_forge_metabolism

# 888_JUDGE — Sovereign constitutional verdict
from arifosmcp.helix.organs.inner.judge import apex_judge_metabolism

# 999_VAULT — Immutable ledger commitment
from arifosmcp.helix.organs.inner.vault import vault_seal_metabolism


__all__ = [
    "init_anchor_metabolism",
    "agi_reason_metabolism",
    "agi_reflect_metabolism",
    "asi_simulate_metabolism",
    "asi_critique_metabolism",
    "agi_asi_forge_metabolism",
    "apex_judge_metabolism",
    "vault_seal_metabolism",
]
