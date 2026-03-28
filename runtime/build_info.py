"""Build information for arifOS AAA MCP."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .public_registry import release_version_label


def get_build_info() -> dict[str, Any]:
    """Return version and environment metadata — live timestamp on every call."""
    return {
        "version": release_version_label(),
        "commit": "ab774bf8",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "FORGED",
        "forge_date": "2026-03-22",
        "forge_word": "FORGE",
    }
