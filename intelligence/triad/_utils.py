"""
arifosmcp.intelligence/triad/_utils.py — Shared triad utilities

Internal helpers shared across delta/omega/psi triad modules.
"""

from __future__ import annotations

from typing import Any, Protocol


class _FloorConcernLike(Protocol):
    """Structural protocol for FloorConcern-compatible objects."""

    floor_id: str
    passed: bool
    score: float
    reason: str


def serialize_floor_concerns(floor_concerns: list[_FloorConcernLike]) -> list[dict[str, Any]]:
    """Serialize a list of FloorConcern objects to plain dicts for JSON output."""
    return [
        {
            "floor_id": fc.floor_id,
            "passed": fc.passed,
            "score": fc.score,
            "reason": fc.reason,
        }
        for fc in floor_concerns
    ]
