"""
Constitutional Runtime Modes (F7 Humility enforcement)

arifOS v65.0-DEV — Explicit Degradation Mode
F2 Truth: We acknowledge infrastructure gaps
"""

import sys
from enum import Enum


class ConstitutionalMode(Enum):
    """Constitutional enforcement levels based on infrastructure."""

    SOVEREIGN = "sovereign"  # PostgreSQL + Redis + ZDR + full F12
    DEGRADED = "degraded"  # SQLite + memory (current reality)
    MOCK = "mock"  # Unit tests only (previous false state)


# Runtime Configuration (F2 Truth — explicit degradation)
CONFIG = {
    "mode": ConstitutionalMode.DEGRADED,
    "vault_backend": "sqlite",  # F1: Reversible (can migrate to postgres)
    "session_backend": "memory",  # F1: Ephemeral but functional
    "mcp_protocol": "stdio",  # Local-first
    "f12_wall_active": False,  # F4: Don't pretend defense exists
    "tri_witness_active": False,  # F3: Only 1 witness (AI)
    "human_escalation": "telegram_bot",  # Manual 888 Judge (kau)
}


def announce_startup():
    """Constitutional startup announcement (F2 Truth)."""
    sys.stderr.write("=" * 60 + "\n")
    sys.stderr.write("arifOS Constitutional AI Governance System\n")
    sys.stderr.write("=" * 60 + "\n")
    sys.stderr.write(f"[MODE] {CONFIG['mode'].value.upper()}\n")
    sys.stderr.write(f"[VAULT] {CONFIG['vault_backend']} (NOT cryptographically sealed)\n")
    sys.stderr.write(f"[SESSION] {CONFIG['session_backend']} (ephemeral)\n")
    sys.stderr.write(
        f"[F12] {'ACTIVE' if CONFIG['f12_wall_active'] else 'INACTIVE — external tools disabled'}\n"
    )
    sys.stderr.write(f"[F3] {'Tri-Witness' if CONFIG['tri_witness_active'] else 'Single-Witness (AI only)'}\n")
    sys.stderr.write(f"[888] Human escalation via: {CONFIG['human_escalation']}\n")
    sys.stderr.write("-" * 60 + "\n")
    sys.stderr.write("WARNING: Limited constitutional enforcement in DEV_MODE\n")
    sys.stderr.write("DO NOT deploy to production without SOVEREIGN mode\n")
    sys.stderr.write("=" * 60 + "\n")


def get_mode() -> ConstitutionalMode:
    """Get current constitutional mode."""
    return CONFIG["mode"]


def is_sovereign() -> bool:
    """Check if running in sovereign mode."""
    return CONFIG["mode"] == ConstitutionalMode.SOVEREIGN


def require_sovereign(feature: str):
    """Decorator to require sovereign mode for feature."""
    if not is_sovereign():
        raise RuntimeError(
            f"Feature '{feature}' requires SOVEREIGN mode. Current mode: {CONFIG['mode'].value}"
        )
