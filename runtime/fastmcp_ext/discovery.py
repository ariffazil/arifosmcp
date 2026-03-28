"""Discovery metadata builders for AAA MCP."""

from __future__ import annotations

from typing import Any


def build_surface_discovery(tools: list[str]) -> dict[str, Any]:
    """Build lightweight discovery payload for resources/prompts/clients."""
    return {
        "surface": "arifOS_AAA_MCP",
        "tool_count": len(tools),
        "tools": tools,
        "contracts": {
            "continuity": "session_id required for governed tools",
            "axioms": ["A1_TRUTH_COST", "A2_SCAR_WEIGHT", "A3_ENTROPY_WORK"],
        },
    }
